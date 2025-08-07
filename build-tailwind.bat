@echo off
echo Compilation de Tailwind CSS...
node .\node_modules\tailwindcss\lib\cli.js -i .\static\css\input.css -o .\static\css\output.css --watch
pause
