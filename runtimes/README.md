## Runtimes

A set of runtime environments the Workers may interact with.
Each runtime is configured to be a docker container / VM,
with control via shell or other interfaces given to the AI.

## Running

All commands executed within `runtimes/` directory.
These commands prepare the envs, execution is performed within python.

### Prepare

- **linux**:
    - If re-building: `docker kill linux-shell`
    - Run: `docker build -t linux ./linux`

### Test run

- **linux**:
    - Run: `docker run -i --rm --network=none --cpus="0.5" --memory="128m" --cap-drop=ALL linux`

> Todo: Integrate docker set-up into the python script.

