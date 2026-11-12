"""Class identity and declaration relationships are not same-name equivalence."""
import copy
import gc
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import types
import weakref

import pytest

ROOT = Path(__file__).parents[2]
spec = importlib.util.spec_from_file_location('class_graph_census', ROOT/'scripts/census_runtime_api.py')
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)


def installed(monkeypatch, **exports):
    module = types.ModuleType('class_graph_fixture')
    module.__all__ = list(exports)
    vars(module).update(exports)
    monkeypatch.setitem(sys.modules, module.__name__, module)
    return module


def test_same_named_classes_cannot_merge_inherited_method_owner_contracts(monkeypatch):
    class Base:
        def execute(self, point):
            pytest.fail('Reference method executed')
    first = type('Twin', (Base,), {'__module__': 'class_graph_fixture'})
    second = type('Twin', (Base,), {'__module__': 'class_graph_fixture'})
    assert first is not second and first.execute is second.execute
    installed(monkeypatch, First=first, Second=second)
    census = runtime.RuntimeCensus('fixture')
    census.module('class_graph_fixture')
    methods = [row for row in census.result()['records'] if row['kind'] == 'method'
        and any(path.endswith('.execute') for path in row['exposures'])]
    assert len(methods) == 2
    assert {tuple(row['exposures']) for row in methods} == {
        ('class_graph_fixture.First.execute',), ('class_graph_fixture.Second.execute',)}
    assert len({row['owner_class'] for row in methods}) == 2


def test_static_class_labels_do_not_execute_metaclass_module_properties():
    calls = []
    class Meta(type):
        @property
        def __module__(cls):
            calls.append('executed')
            return 'fabricated'
    class Owner(metaclass=Meta):
        pass
    name = runtime.type_name(Owner)
    assert calls == []
    assert name == __name__+'.'+Owner.__qualname__


def collect(monkeypatch, **exports):
    installed(monkeypatch, **exports)
    census = runtime.RuntimeCensus('fixture')
    census.module('class_graph_fixture')
    result = census.result()
    runtime.validate_class_graph(result)
    return census, result


def test_shared_raw_method_keeps_two_distinct_class_contexts_in_one_function_identity_group(monkeypatch):
    class Base:
        def execute(self, point):
            pytest.fail('Reference method executed')
    first = type('Twin', (Base,), {'__module__': 'class_graph_fixture'})
    second = type('Twin', (Base,), {'__module__': 'class_graph_fixture'})
    _, result = collect(monkeypatch, First=first, Second=second, Alias=second)
    methods = [row for row in result['records'] if row['kind'] == 'method'
        and any(path.endswith('.execute') for path in row['exposures'])]
    assert len(methods) == len({row['owner_class_identity'] for row in methods}) == 2
    assert len({row['declaring_class_identity'] for row in methods}) == 1
    assert len({row['object_identity_group'] for row in methods}) == 1
    assert all(row['inherited'] for row in methods)
    assert sorted(len(row['exposures']) for row in methods) == [1, 2]
    classes = [row for row in result['records'] if row['kind'] == 'class']
    assert len(classes) == 2 and len({row['canonical_id'] for row in classes}) == 1
    assert {row['id'] for row in classes} == {row['owner_class'] for row in methods}
    runtime.validate_object_identity_groups(result)


def test_equal_base_labels_do_not_merge_distinct_unexported_class_objects(monkeypatch):
    first = type('Hidden', (), {'__module__': 'class_graph_fixture'})
    second = type('Hidden', (), {'__module__': 'class_graph_fixture'})
    left, right = type('Child', (first,), {}), type('Child', (second,), {})
    _, result = collect(monkeypatch, Left=left, Right=right)
    nodes = result['class_graph']['nodes']
    hidden = [node for node in nodes if node['names'] == ['class_graph_fixture.Hidden']]
    assert len(hidden) == 2 and hidden[0]['id'] != hidden[1]['id']
    assert all(node['record_ids'] == [] for node in hidden)
    classes = [row for row in result['records'] if row['kind'] == 'class']
    assert {row['direct_base_identities'][0] for row in classes} == {node['id'] for node in hidden}


def test_direct_bases_order_mro_and_metaclass_are_distinct_relationships(monkeypatch):
    class Root:
        pass
    class Left(Root):
        pass
    class Right(Root):
        pass
    class Meta(type):
        def create(cls, point):
            pytest.fail('Metaclass method executed')
    class Child(Left, Right, metaclass=Meta):
        pass
    _, result = collect(monkeypatch, Child=Child)
    nodes = {node['id']: node for node in result['class_graph']['nodes']}
    row, = [row for row in result['records'] if row['kind'] == 'class']
    observation, = nodes[row['class_identity']]['topology_observations']
    name = lambda identity: nodes[identity]['names'][0]
    assert list(map(name, observation['direct_bases'])) == list(map(runtime.type_name, (Left, Right)))
    assert list(map(name, observation['mro'])) == list(map(runtime.type_name, Child.__mro__))
    assert name(observation['metaclass']) == runtime.type_name(Meta)
    method, = [row for row in result['records'] if row['id'].endswith('@type.create')]
    assert method['owner_class_identity'] == row['class_identity']
    assert method['declaring_class_identity'] == row['metaclass_identity']
    assert method['lookup_plane'] == 'metaclass'


def test_graph_keeps_declaring_module_file_hash_without_claiming_class_body_provenance(tmp_path, monkeypatch):
    file = tmp_path/'__init__.py'
    file.write_text('# declaration-module fixture\n')
    class Owner:
        pass
    Owner.__module__ = 'class_graph_fixture'
    module = installed(monkeypatch, Owner=Owner)
    module.__file__ = str(file)
    census = runtime.RuntimeCensus('fixture')
    census.module('class_graph_fixture')
    result = census.result()
    runtime.validate_class_graph(result)
    row, = [row for row in result['records'] if row['kind'] == 'class']
    node, = [node for node in result['class_graph']['nodes'] if node['id'] == row['class_identity']]
    source = node['sources']['class_graph_fixture']
    assert source == dict(file='class_graph_fixture/__init__.py',
        source_hash=hashlib.sha256(file.read_bytes()).hexdigest(), source_hash_scope='module_file')
    assert not node['declaration_body_provenance_verified']
    assert all(item['status'] == 'unverified' and item['native_mapping'] is None for item in result['records'])


def test_deferred_class_signature_does_not_merge_member_contexts_or_drop_class_graph(monkeypatch):
    class Meta(type):
        @property
        def __signature__(cls):
            pytest.fail('Class signature descriptor executed')
    class Base:
        def execute(self):
            pytest.fail('Reference method executed')
    first = Meta('Twin', (Base,), {'__module__': 'class_graph_fixture'})
    second = Meta('Twin', (Base,), {'__module__': 'class_graph_fixture'})
    _, result = collect(monkeypatch, First=first, Second=second)
    assert not [row for row in result['records'] if row['kind'] == 'class']
    methods = [row for row in result['records'] if row['id'].endswith('.execute')]
    assert len(methods) == len({row['owner_class_identity'] for row in methods}) == 2
    assert all(row['still_in_scope'] for row in result['unresolved'] if row.get('deferred'))


def test_static_class_identity_traversal_does_not_execute_hostile_metaclass_layout_getters(monkeypatch):
    class Meta(type):
        def __getattribute__(cls, name):
            pytest.fail('Dynamic metaclass attribute lookup executed: '+name)
    class Owner(metaclass=Meta):
        def execute(self):
            pytest.fail('Reference method executed')
    census, result = collect(monkeypatch, Owner=Owner)
    assert census.class_identity(Owner, 'class_graph_fixture') in {
        node['id'] for node in result['class_graph']['nodes']}
    assert any(row['id'].endswith('.execute') for row in result['records'])
    assert any(row.get('deferred') for row in result['unresolved'])


def test_type_labels_never_read_an_instances_spoofed_class_attribute():
    class Value:
        def __getattribute__(self, name):
            pytest.fail('Instance attribute executed: '+name)
    assert runtime.type_name(Value()) == runtime.type_name(Value)


@pytest.mark.parametrize('name,attribute', [('MT19937', 'jumped'), ('PCG64', 'advance'),
    ('Philox', 'spawn'), ('SFC64', 'random_raw'), ('Generator', 'normal')])
def test_native_extension_metaclass_labels_keep_real_cython_descriptor_contracts(name, attribute):
    import numpy as np
    owner = getattr(np.random, name)
    descriptor = next(runtime._class_field(base, '__dict__')[attribute]
        for base in runtime._class_field(owner, '__mro__')
        if attribute in runtime._class_field(base, '__dict__'))
    cls = type(descriptor)
    assert runtime.type_name(cls) == (type.__getattribute__(cls, '__module__')+'.'
        +type.__getattribute__(cls, '__qualname__'))
    census = runtime.RuntimeCensus('fixture')
    census.class_members(owner, 'numpy.random.'+name, 'numpy')
    result = census.result()
    runtime.validate_class_graph(result)
    exposure = 'numpy.random.'+name+'.'+attribute
    assert any(exposure in row['exposures'] for row in result['records'])
    assert not any(row['id'] == exposure and row['kind'] == 'member_introspection_failed'
        for row in result['unresolved'])


def test_class_objects_are_retained_until_graph_observation_finishes():
    value = type('Ephemeral', (), {})
    reference = weakref.ref(value)
    census = runtime.RuntimeCensus('fixture')
    identity = census.class_identity(value, 'fixture')
    del value
    gc.collect()
    assert reference() is not None
    assert identity in {node['id'] for node in census.result()['class_graph']['nodes']}
    del census
    gc.collect()
    assert reference() is None


def test_class_graph_results_are_detached_and_repeated_calls_do_not_mutate_held_metadata(monkeypatch):
    class Owner:
        pass
    census, before = collect(monkeypatch, Owner=Owner)
    expected = copy.deepcopy(before['class_graph'])
    before['class_graph']['nodes'].clear()
    assert census.result()['class_graph'] == expected
    assert census.result()['class_graph'] == expected


def test_changed_class_topology_keeps_both_observations_and_requires_review():
    class Base:
        pass
    class Alternative:
        pass
    class Owner(Base):
        pass
    census = runtime.RuntimeCensus('fixture')
    identity = census.class_identity(Owner, 'fixture')
    Owner.__bases__ = (Alternative,)
    assert census.class_identity(Owner, 'fixture', observe=True) == identity
    result = census.result()
    runtime.validate_class_graph(result)
    node, = [node for node in result['class_graph']['nodes'] if node['id'] == identity]
    assert len(node['topology_observations']) == 2
    assert any(row['id'] == identity and row['kind'] == 'class_topology_changed'
        and row['review_required'] for row in result['unresolved'])


def part(tmp_path, label, value):
    value = copy.deepcopy(value)
    value['modules'] = [dict(name=label, version='fixed')]
    source, receipt = tmp_path/(label+'.json.gz'), tmp_path/(label+'-terminal.json')
    source.write_bytes(gzip.compress(json.dumps(value).encode()))
    receipt.write_text(json.dumps(dict(profile='fixture', isolation=label, terminal=True, exit=0,
        artifact_sha256=hashlib.sha256(source.read_bytes()).hexdigest(), modules=[label])))
    return source, receipt


def test_isolated_graphs_relabel_every_record_and_edge_without_cross_worker_identity(tmp_path, monkeypatch):
    class Owner:
        class Child:
            pass
        def execute(self):
            pytest.fail('Reference method executed')
    Owner.Child.Owner = Owner
    _, value = collect(monkeypatch, Owner=Owner)
    original = copy.deepcopy(value)
    result = runtime.merge_isolated_files('fixture', [part(tmp_path, name, value) for name in ('left', 'right')])
    runtime.validate_class_graph(result)
    runtime.validate_object_identity_groups(result)
    assert len(result['class_graph']['nodes']) == 2*len(value['class_graph']['nodes'])
    for node in result['class_graph']['nodes']:
        suffix = '@isolated-'+node['collection_isolation']
        assert node['id'].endswith(suffix)
        assert all(key.endswith(suffix) for key in node['record_ids'])
        for observation in node['topology_observations']:
            assert all(key.endswith(suffix) for key in [*observation['mro'], *observation['direct_bases'], observation['metaclass']])
    assert all(not audit['cross_process_identity_verified'] for audit in result['class_graph_audits'])
    assert value == original


def test_legacy_graph_absence_stays_unknown_and_cannot_be_mixed_with_new_graphs(tmp_path, monkeypatch):
    _, value = collect(monkeypatch)
    legacy = copy.deepcopy(value)
    del legacy['class_graph']
    result = runtime.merge_isolated_files('fixture', [part(tmp_path, 'legacy', legacy)])
    assert 'class_graph' not in result and result['class_graph_audits'][0]['observed'] is False
    with pytest.raises(ValueError, match='Mixed class graph'):
        runtime.merge_isolated_files('fixture', [part(tmp_path, 'old', legacy), part(tmp_path, 'new', value)])


@pytest.mark.parametrize('fault', ['schema_bool', 'basis', 'behavior', 'body_provenance', 'atomicity',
    'cross_process', 'duplicate_node', 'unknown_mro', 'wrong_mro_owner', 'missing_base', 'unknown_meta',
    'unknown_record', 'omitted_record', 'record_identity', 'declaring_identity', 'missing_graph', 'null_graph'])
def test_malformed_class_graphs_cannot_acquire_a_provenance_claim(monkeypatch, fault):
    class Owner:
        def execute(self):
            pytest.fail('Reference method executed')
    _, value = collect(monkeypatch, Owner=Owner)
    graph = value['class_graph']
    row, = [row for row in value['records'] if row['kind'] == 'class']
    node, = [node for node in graph['nodes'] if node['id'] == row['class_identity']]
    observation = node['topology_observations'][0]
    if fault == 'schema_bool':
        graph['schema'] = True
    elif fault == 'basis':
        graph['basis'] = 'same_qualified_name'
    elif fault in {'behavior', 'body_provenance', 'atomicity', 'cross_process'}:
        graph[dict(behavior='behavior_verified', body_provenance='declaration_body_provenance_verified',
            atomicity='topology_atomicity_verified', cross_process='cross_process_identity_verified')[fault]] = True
    elif fault == 'duplicate_node':
        graph['nodes'].append(copy.deepcopy(node))
    elif fault == 'unknown_mro':
        observation['mro'].append('unknown')
    elif fault == 'wrong_mro_owner':
        observation['mro'] = observation['mro'][1:]
    elif fault == 'missing_base':
        observation['direct_bases'] = [node['id']]
    elif fault == 'unknown_meta':
        observation['metaclass'] = 'unknown'
    elif fault == 'unknown_record':
        node['record_ids'].append('unknown')
    elif fault == 'omitted_record':
        node['record_ids'].clear()
    elif fault == 'record_identity':
        row['class_identity'] = 'unknown'
    elif fault == 'declaring_identity':
        method, = [row for row in value['records'] if row['id'].endswith('.execute')]
        method['declaring_class_identity'] = 'unknown'
    elif fault == 'missing_graph':
        del value['class_graph']
    else:
        value['class_graph'] = None
    with pytest.raises(ValueError, match='[Cc]lass graph'):
        runtime.validate_class_graph(value)


def test_progress_projection_preserves_graph_links_without_implementation_acceptance(tmp_path, monkeypatch):
    class Owner:
        def execute(self):
            pytest.fail('Reference method executed')
    _, value = collect(monkeypatch, Owner=Owner)
    artifact = tmp_path/'runtime-api.json'
    artifact.write_text(json.dumps(value))
    spec = importlib.util.spec_from_file_location('class_graph_builder', ROOT/'scripts/build_engineering_progress.py')
    builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)
    rows, audits = builder.runtime_census([artifact])
    assert audits[0]['class_graph'] == value['class_graph']
    method, = [row for row in rows if row['id'].endswith('.execute')]
    assert method['runtime_observations'][0]['owner_class_identity']
    assert method['runtime_observations'][0]['declaring_class_identity']
    assert all(row['status'] == 'unverified' and row['native_mapping'] is None for row in rows)
