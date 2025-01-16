@echo off
docker build -t chat-im .
timeout /t 5 /nobreak
docker create --name chat-cont --volume=D:\payg_generated\history:/PayAsYouGoChat/history --volume=D:\payg_generated\images:/PayAsYouGoChat/images -p 7860:7860 chat-im:latest