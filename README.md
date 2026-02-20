# IDP

Code and issue / progress tracking for IDP team 112.

## Code

- All code should be first done on branches before being merged to main via a pull request. **Do not push directly to main**.
- Pull requests should be reviewed by at least one person other than yourself to aid team understanding and to get a fresh perspective.
- Investigation code should never be merged to main, it should remain on branches until formalised and ready for production.
- Branches can be created from / merged into other branches so an integration issue can be created from the investigation issue.
  - _Example: initial PD control shouldn't be merged to main, the formal integration should first be done before the result it merged to main._

## Issues

Purpose:
- Helps us scaffold our progress and understand what is blocking us.
- Makes presentations much easier to prepare as our progress is easily trackable.
- Faster progress: we're all busy and want to waste as little time as possible while still achieving a good result.

_Note: this doesn't replace Gantt charts, it's simply a more verbose representation of it. We can translate issues / milestones easily into a Gantt chart._

### Creating issues

Everyone should raise issues for things or problems that we need to solve in order to keep progressing.

- They can be minimal while starting but no work should ideally be done undocumented as it makes it harder to track progress.

**It should not take longer than 5 minutes to raise an issue. If it does, break it into sub issues.**

Issues **should**:
- List prerequisites that need doing before we start progress on the issue.
  -  There is a relationship option, I.E basic motor control is _blocked_ by set up picobot.
- Have a good description of the problem. Words are cheap, detail help convey the problem fully to others.
- Have a definition of done. This means listing explicitly *everything* that needs to be completed in order for the issue to be considered done.
- Assign the sub team needed to work on the issues as labels. Multiple teams can be assigned this way. The labels (presently) are: software, electrical, and mechanical.
- Have a milestone so we know what we need it for. I.E PD control is under the 'basic line following' milestone.
  - _New milestones should be created as needed_.

### Working on issues

- If you want to work on an issue, you should assign it to yourself. Multiple people can work on an issue.
- Ideally issues from the current milestone that aren't blocked should be worked on first. You can sort by milestone in the issues tab.
  - This means you become the _owner_ for the problem, I.E you are responsible for it. 
  - _Issues should be a collaborative effort! If you're stuck ask for help._
- If an issue is too large, sub issues can be created to make the issue more managable.
- **Please track progress / results as comments on the issue. It will make understanding progress much easier + presentations much easier**.
- When an issue is considered to be complete, the inital creator & any people familiar with the issue should be consulted and any merge (pull) requests should be reviewed.
- Any additional issues can be raised as sub issue. When the ticket is considered by everyone to be complete it *should* be closed.





