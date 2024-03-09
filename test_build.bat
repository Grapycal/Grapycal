CALL conda deactivate &&^
CALL conda env remove -n gr-test &&^
CALL conda create  -y -n gr-test python=3.11 &&^
CALL conda activate gr-test &&^
CALL pip install backend\dist\grapycal-0.11.3-py3-none-any.whl &&^
CALL pip install extensions\grapycal_builtin\dist\grapycal_builtin-0.11.3-py3-none-any.whl &&^
CALL grapycal