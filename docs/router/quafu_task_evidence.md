# Quafu Task-List Evidence

This is the concrete proof boundary for the Router idea.

## What Was Verified From The Public Quafu Site

The provided task page loads a Vue/Element Plus task table from:

- `https://quafu-sqc.baqis.ac.cn/framework/tasks`
- JavaScript bundle: `/static/assets/D_yeVeah.js`

The task page calls:

- `GET /api/tasks`
- `GET /api/task-status/{taskId}`
- `PATCH /api/task/{taskId}` for cancel
- `DELETE /api/task/{taskId}` for delete
- `PATCH /api/task-select/{taskIds}` for selected cancel
- `DELETE /api/task-select/{taskIds}` for selected delete

The Router evidence adapter only uses the read-only task list shape:

```json
{
  "items": [
    {
      "taskId": "string",
      "taskName": "string",
      "chipName": "Baihua",
      "status": "Pending",
      "submitTime": "2026-06-13-10-00-00"
    }
  ],
  "total": 1
}
```

The public frontend exposes these task-table columns:

- `Task ID`
- `Task Name`
- `Chip`
- `Status`
- `Submit Time`

The public frontend exposes these chip filters:

- `Baihua`
- `Dongling`
- `Haituo`
- `Yunmeng`
- `Miaofeng`
- `Yudu`
- `Hongluo`

The public frontend exposes these statuses:

- `Submitted`
- `Transpiled`
- `Pending`
- `Canceled`
- `Failed`
- `Finished`

Unauthenticated API access returns HTTP 401 with `Authentication is required,
please login`. That is good security, and it means live proof requires an
authorized login or a user-exported JSON response.

## Why This Proves A Real Gap

The existing task page is an after-submission task table. It shows where a task
went and what happened after submission.

The Router product sits before submission. It uses the same observed fields to
estimate per-chip queue pressure, then chooses a chip before the job is sent.
With calibration and result data added later, it becomes a paid decision layer:

- "Do not send this task to the crowded chip."
- "Choose the chip whose queue/fidelity tradeoff fits this SLA."
- "Generate an audit report explaining why this backend was selected."

## Local Verification

```bash
python3 -m quantumbridge.router quafu-tasks \
  --input examples/quafu_tasks_sample.json \
  --route-workload bell
```

For real proof, replace `examples/quafu_tasks_sample.json` with an authorized
Quafu `/api/tasks` export. The code does not need a Quafu token in the repo and
does not submit, cancel, or delete jobs.

The default fidelity threshold is intentionally loose for this command because
`/api/tasks` proves queue pressure, not calibration quality. Tight fidelity
routing requires authorized calibration or result-history data in the next PoC
step.
