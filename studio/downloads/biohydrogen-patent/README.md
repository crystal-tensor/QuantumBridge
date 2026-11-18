# Biohydrogen reproducible study

Author: 曾祥洪 --QuantumBridge研发组

Run from the repository root after installing the native project and the recorded numerical environment:

```sh
python -m pip install -e .
python -m pip install -r requirements/constraints-biohydrogen.txt
python -m scripts.biohydrogen_patent_model --output studio/downloads/biohydrogen-patent
python -m scripts.biohydrogen_process_model --output studio/downloads/biohydrogen-patent
python scripts/build_biohydrogen_case.py
python -m pytest tests/applications/test_biohydrogen_patent_model.py tests/applications/test_biohydrogen_process_model.py tests/applications/test_biohydrogen_hardware_evidence.py -q
node studio/scripts/serve.mjs
```

Enter through framework.html > science > chemistry. The paired notebook reruns local models and reads recorded hardware measurements without submitting tasks.

Eight Baihua hardware tasks used 1024 shots per basis. Angles were optimized locally then evaluated on the device. Raw hardware bias is retained; finite-shot standard errors are not device-accuracy certificates. The normalized process model is not fitted biology and does not predict physical yield.

The film uses Anima geometry, local LTX-2.3 opening imagery, Xiaoxiao narration and an original procedural audio bed. Editable film sources and citations are included in source.zip. Intermediate frame renders and local credential files are excluded.
