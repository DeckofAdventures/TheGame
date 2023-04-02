# For use in the event new yaml specs are created

# For each file in the Mechanics folder ending in yaml
for f in $(ls -f ../../docs/src/1_Mechanics/*yaml); do
    # link from that folder to the current folder with the same filename
    # -s is soft link.  -f is force, deleting existing version
    ln -sf $f ./${f##*/}
done
