CALL conda deactivate &&^
CALL conda env remove -n gr-test &&^
CALL conda create  -y -n gr-test python=3.11 &&^
CALL conda activate gr-test &&^
CALL pip install grapycal grapycal_builtin
CALL grapycal