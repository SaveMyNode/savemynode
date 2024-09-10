# CONTRIBUTION

The flow of contribution to the main branch can be divided into 3 major steps:

## Cloning the first time

1. Cloning the repository (main branch)
2. Fix any particular issue (two at a time is fine if it doesnt lead any changes that lead to merge conflicts)
3. Check out to a new branch (preferrably `name-dev`) and push all changes there

The commands to checkout to a new branch and pushing to it are:

```sh 
git add .
git commit -m "<yourmsg>"
git checkout -b "<branch-name>"
git push --set-upstream origin "<branch-name>"
```

## Fixing your own branch 

Ensure that you are fixing your OWN branch ONLY, if you do not have a branch check out `Cloning the first time`

## Commits

The commit message should follow the convention:

```sh 
["<commit-type>"] "<commit-msg>" "<issue no>"
```

```md 
[FEAT]  -- For a feature
[CHORE] -- For fixing any past errors or just a small commit 
[VULN]  -- Fixing any vulnerability or CWEs
[MERGE] -- Commit responsible for dealing with merging
[TEST]  -- Commits designed to adding test/benchmarking related code
```
Example: `[FEAT] Created xxxx #42`

Try to keep the commit msg short and concise, not more than **10 words**


## Merging


