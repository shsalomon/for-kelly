# Kelly's Lab Meeting Prep Agent

A small Backboard-powered command-line agent that turns neuroscience research notes,
paper abstracts, or early results into an organized lab-meeting brief. It keeps a
conversation for Kelly between runs, making it useful for refining a presentation or
returning to an ongoing project.

## Setup

1. Create and activate a virtual environment.
2. Install the dependency:

	```bash
	python -m pip install -r requirements.txt
	```

3. Export a Backboard API key. The key is read only from the environment and is never
	stored in source code:

	```bash
	export BACKBOARD_API_KEY="your_key_here"
	```

## Use

Give the agent notes directly:

```bash
python lab_meeting_prep.py "We used two-photon calcium imaging in mouse V1..."
```

Or send longer notes through standard input:

```bash
python lab_meeting_prep.py <<'NOTES'
Question: Does locomotion alter orientation tuning in layer 2/3 neurons?
Methods: Head-fixed mice, visual gratings, calcium imaging.
Preliminary result: Responses appeared larger during running in 4 of 6 animals.
NOTES
```

The resulting brief includes a takeaway, background, methods, findings,
interpretation, limitations, discussion questions, and next steps. Use `--reset` to
start a clean meeting conversation while keeping the same specialized assistant.

The local `.lab_meeting_prep_state.json` file contains only Backboard assistant and
thread IDs; it is ignored by git.