REM Update Fork
git remote add upstream https://github.com/home-assistant/core.git
git fetch upstream
git checkout dev
git merge upstream/dev
git push