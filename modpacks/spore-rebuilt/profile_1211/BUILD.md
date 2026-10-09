# RC1 build checkpoint

The frozen installer index is modrinth.index.json; VALIDATION_RC1.json records the actual test.
Do not run resolve.py as a release build: it refreshes catalog metadata, which can choose different versions. Modrinth currently lists an older MCA compat file that failed runtime testing. The tested replacement is pinned in external-files.json and embedded in the installer.

The user-supplied gun archives are private build inputs at ../source_1211/overrides/tacz. They are deliberately not published to GitHub. Final modified copies are inside the user deliverable. Other jars are downloaded by URL and verified by hashes.

Overrides in this directory are the final tested configuration. configure.py and fix_resources.py are development generators; configure.py resets some manual corrections. Use the checked-in overrides for this RC, not regenerated draft settings.

Legacy manifest scripts in the parent directory are obsolete drafts and must not be used for installation.
