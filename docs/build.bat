@ECHO OFF

if "%1" == "" (
    goto help
)

if "%2" == "" (
    goto help
)

if "%1" == "-l" (

    if "%4" == "true" (
        goto buildw
    )

    goto build
)

if "%2" == "true" (
    goto install
)

REM Command file for Sphinx documentation

if "%SPHINXBUILD%" == "" (
	set SPHINXBUILD=sphinx-build
)
set BUILDDIR=_build
set ALLSPHINXOPTS=-d %BUILDDIR%/doctrees %SPHINXOPTS% .
set I18NSPHINXOPTS=%SPHINXOPTS% .
if NOT "%PAPER%" == "" (
	set ALLSPHINXOPTS=-D latex_paper_size=%PAPER% %ALLSPHINXOPTS%
	set I18NSPHINXOPTS=-D latex_paper_size=%PAPER% %I18NSPHINXOPTS%
)
if "%1" == "help" (
	:help
	echo.Please use `.\build ^<-^>` where ^<-^> must be one of these
	echo.  -l   language to build.
	echo.  -w   file to write errors.
    echo.  -i   installs all required dependencies. 
	goto end
)


REM Check if sphinx-build is available and fallback to Python version if any
%SPHINXBUILD% 2> nul
if errorlevel 9009 goto sphinx_python
goto sphinx_ok

:sphinx_python

set SPHINXBUILD=python -m sphinx.__init__
%SPHINXBUILD% 2> nul
if errorlevel 9009 (
	echo.
	echo.The 'sphinx-build' command was not found. Make sure you have Sphinx
	echo.installed, then set the SPHINXBUILD environment variable to point
	echo.to the full path of the 'sphinx-build' executable. Alternatively you
	echo.may add the Sphinx directory to PATH.
	echo.
	echo.If you don't have Sphinx installed, grab it from
	echo.http://sphinx-doc.org/
	exit /b 1
)

:sphinx_ok


:build
sphinx-build -b html . _build/html/%2 -D language=%2
goto end

:buildw
sphinx-build -b html . _build/html/%2 -D language=%2 -w sphinx-errors.txt
goto end

:install 
pip install -U sphinx
pip install -U sphinx-build
pip install -U sphinxcontrib_trio
goto end

:end
