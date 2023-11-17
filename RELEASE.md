<!-- SPDX-License-Identifier: MIT -->

# Release Procedure

This document provides general information and steps about the project's release procedure.  
If you're reading this, this will likely not be useful to you, unless you have administrator permissions in the repository or want to replicate this setup in your own project :p

The process is largely automated, with manual action only being needed where higher permissions are required.  
Note that pre-releases (alpha/beta/rc) don't quite work with the current setup; we don't currently anticipate making pre-releases, but this may still be improved in the future.


## Steps

These steps are mostly equivalent for major/minor (feature) and micro (bugfix) releases.  
The branch should be `master` for major/minor releases and e.g. `1.2.x` for micro releases.

1. Run the `Create Release PR` workflow from the GitHub UI (or CLI), specifying the correct branch and new version.
    1. Wait until a PR containing the changelog and version bump is created. Update the changelog description and merge the PR.
    2. In the CLI, fetch changes and create + push a tag for the newly created commit, which will trigger another workflow.
        - [if latest] Also force-push a `stable` tag for the same ref.
    3. Update the visibility of old/new versions on https://readthedocs.org.
2. Approve the environment deployment when prompted, which will push the package to PyPI.
    1. Update and publish the created GitHub draft release, as well as a Discord announcement. 🎉
3. [if major/minor] Create a `v1.2.x` branch for future backports, and merge the newly created dev version PR.


### Manual Steps

If the automated process above does not work for some reason, here's the abridged version of the manual release process:

1. Update version in `__init__.py`, run `towncrier build`. Commit, push, create + merge PR.
2. Follow steps 1.ii. + 1.iii. like above.
3. Run `python -m build`, attach artifacts to GitHub release.
4. Run `twine check dist/*` + `twine upload dist/*`.
5. Follow steps 2.i. + 3. like above.


## Repository Setup

This automated process requires some initial one-time setup in the repository to work properly:

1. Create a GitHub App ([docs](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/making-authenticated-api-requests-with-a-github-app-in-a-github-actions-workflow)), enable write permissions for `content` and `pull_requests`.
2. Install the app in the repository.
3. Set repository variables `GIT_APP_USER_NAME` and `GIT_APP_USER_EMAIL` accordingly.
4. Set repository secrets `BOT_APP_ID` and `BOT_PRIVATE_KEY`.
5. Create a `release-pypi` environment, add protection rules.
6. Set up trusted publishing on PyPI ([docs](https://docs.pypi.org/trusted-publishers/adding-a-publisher/)).
