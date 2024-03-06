## v0.11.0 (2024-03-06)

### Feat

- allow pasting images or code with ctrl v
- better UI animation
- add demo
- docker compose demo
- demo on docker desktop kubernetes
- allow interrupting
- notification
- restore all attrs and ctrls by default
- merge build_node and init_node into create()
- network save and load
- TrainNode and ConfigureNode
- singleton node and expose attributes globally
- add optionControl
- let ValuedControl able to invoke edge_activated
- display if ports accept more edges
- placeholder
- pass config from webpack; add login api

### Fix

- use generated workspace id instead of pid
- fix node bugs
- optimize node animation communication
- fix bugs of nodes
- fix lineplot performance issue
- remove unused import
- minor change
- change when restore
- change when restore
- make ui text selectable
- correctly propogate event for inactive ports
- listen to keybindings in capture phase
- fix reconnection
- improve logging
- improve logging
- log correctly if no internet
- fix new workspace bug
- allow multi networks in train node
- improve ui
- fix deletion and selection bug
- typo
- clear edges' data on exception
- option control select all
- option control search bug
- fix funcDef
- input box bug
- fix image paste node dimension
- fix runtime bugs
- parallel function call bug
- inconsistent is_new value
- device bug
- refactor grapycal_torch
- is_all_edge_ready returns False if 0 connected edges
- add add_option_control
- misc
- unify looks of controls
- improve autoCompMenu behavior
- make UI better
- fix control-in-port layout bug
- css
- let control take the label of the port
- bump grapycal_torch version
- add missing dep
- improve edge apparance
- fix ui bugs
- distinguish mouse buttons when interact
- make box selection and ctrl/shift compatible
- inspector dragging
- grapycal_torch
- grapycal_torch
- remove debugging prints
- control name bug
- minor css problem
- fix ui alignment
- make controls in input ports restorable

## v0.10.0 (2023-12-30)

### Feat

- copy, paste and cut
- add linter to actions
- test arc runner
- add dev chart
- deploy front using helm chart
- add frontend helm template
- build frontend docker image
- add k8s infra
- shorten the command to only `grapycal`
- push log messages to frontend
- enable add/delete dir or file from file view
- show examples in files tab
- show metadata on UI
- preview node title, markdown description
- DictEditor
- add DictEditor
- display docstring of node on inspector
- add linter ruff.toml

### Fix

- revert linplotcontrol change on b6cf0c8
- improve grapycal_torch
- add things to grapycal_torch
- change box selection to contain mode
- fix paste history structure
- snap nodes when creating
- improve torch extension
- change trainer logic
- ruff.toml
- update data url for repo transfer
- mac ssl cert verified failed
- fix bug caused by last commit
- fix bug
- improve get_remote_extensions
- update unchange code
- add scroll to right side-bar
- use http for submodule url
- add default message for node docstring in nodegen

## v0.9.0 (2023-12-03)

### Feat

- show Welcome.grapycal for new user
- compress .grapycal files with gzip

### Fix

- list Welcome.grapycal in file view
- improve UI
- python 3.12 compatibility
- remove unused files

## v0.8.0 (2023-12-01)

### Feat

- allow opening another workspace
- improve UI
- list extensions on PyPI on the UI

### Fix

- small bug
- config bug
- update package lock
- add dependency
- disallow undoing when big things happen
- fix ctrl c recreating workspace bug
- improve UI
- improve UI
- improve some nodes
- split out grapycal_torch
- update package-lock
- minor fix
- improve development build process
- improve ui
- bypass mime check by removing type=module
- update dependency
- update dependency
- fix bugs

### Refactor

- rearrange project structure to enable production
- place extensions in extensions folder

## v0.7.0 (2023-11-15)

### Feat

- node icon
- changable theme
- abandon fetching process of extensions
- switch from desearialize to manual build
- add tabs to sidebar
- box selection

### Fix

- minor fix
- further unify node height
- add submodule svg
- fix bugs
- make ports well aligned when snapped

### Refactor

- **inspector.ts**: separate inspector and nodeinspector

## v0.6.1 (2023-11-03)

### Fix

- update dependency

## v0.6.0 (2023-11-03)

### Feat

- allow specify http-port
- add linePlotControl

### Fix

- fix bugs

## v0.5.5 (2023-10-29)

### Fix

- improve logging

## v0.5.4 (2023-10-29)

### Fix

- fix syntax

## v0.5.3 (2023-10-29)

### Fix

- move pre_bump.bat
- fix webpage build problem

## v0.5.2 (2023-10-29)

### Fix

- untrack files that should not be tracked
- update build.bat
- include webpage server into grapycal server

## v0.5.1 (2023-10-25)

### Fix

- include webpage in build

## v0.5.0 (2023-10-25)

### Feat

- include webpage server in grapycal server

### Fix

- Ensure version in each file get update

## v0.4.0 (2023-10-04)

## v0.2.0 (2023-06-23)

## v0.1.1 (2023-06-03)
