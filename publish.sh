printf "Current: %s \n" $(git tag --sort=committerdate -l | tail -n 1)
printf "Release: " 
read tag

# Set the latest tag number
sed -i.bak 's|^version = .*$|version = '"'$tag'"'|' setup.py
rm -f setup.py.bak
git add setup.py
git commit -m "Release $tag"
git push

# Tag the new release and push top remote server
git tag $tag 
git push origin --tags
# Create a new release package
rm -rf ./dist
python3 setup.py sdist
pip install twine
twine upload dist/*