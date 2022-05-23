
set USR_INPUT_STR=

set /P USR_INPUT_STR="ŽÀŒ±–¼‚ð“ü—Í": "



for /l %%i in (0,1,23) do (
    START run_python.bat %USR_INPUT_STR% %%i
)