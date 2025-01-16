set container_name=chat-cont
set max_retries=3
set retry_count=0

:retry_start
echo Attempting to start Docker container: %container_name%
docker start %container_name%
if %errorlevel%==0 (
    echo Container started successfully!
    goto open_url
) else (
    set /a retry_count+=1
    echo Failed to start container. Attempt %retry_count% of %max_retries%.
    if %retry_count% geq %max_retries% (
        echo Max retries reached. Exiting script.
        exit /b 1
    )
    timeout /t 5 >nul
    goto retry_start
)
timeout /t 3 /nobreak
:open_url
start "" chrome --new-window --app=http://127.0.0.1:7860/
:check_browser
tasklist | findstr "chrome.exe" >nul
if %errorlevel%==0 (
    timeout /t 5 >nul
    goto check_browser
)

docker stop %container_name%