## Slack Integration Analysis

Part 1 - Current Slack State

1. Database Structure

   The Slack app uses six models to track community activity. SlackUser stores profile data (name, email, avatar), Channel holds channel metadata, and Thread tracks conversation threads separately from channel messages. SlackActivityBucket aggregates daily message counts per user per channel using PostgreSQL upserts, while ChannelUpdateGap enables resumable imports by tracking time ranges that need processing. SeenMessage is a debug-only table used to verify no duplicate counting when the --debug flag is enabled.

2. Data Fetching

   Data is fetched automatically via a daily Celery task at 3:07 AM (config/celery.py lines 86-90), manually through the Django management command ./manage.py fetch_slack_activity with optional channel filtering, or as part of the release report generation workflow (libraries/management/commands/release_tasks.py line 59). All three methods call the same fetch_slack_activity command located in slack/management/commands/fetch_slack_activity.py.

Part 2 - Current Limitations

1. No admin interface - Slack models are not registered in Django admin, so staff cannot view or manage Slack data through the admin UI or manually trigger imports or view import status.

2. Slack users are separate from the main user/contributor system, with no connection between SlackUser and the Email/Identity models, so Slack contributions cannot be tracked as part of overall contributor activity or linked to GitHub contributions or commit authors.

3. Cannot retrieve message content or reactions, only counts - individual messages are not stored (except in debug mode with SeenMessage table), only aggregated daily counts per user per channel are saved, so message content, timestamps, thread context, and reactions (emojis, likes, etc.) are lost after aggregation with no search or filtering of actual message text or analysis of user engagement through reactions.

4. Thread detection gap - some threads may be missed if a reply is sent after the initial import but before the thread is tracked, and only threads with "also send in channel" broadcasts are reliably detected.

5. No real-time updates - data is fetched daily via batch imports, not in real-time, and there is no webhook integration for live updates.

Part 3 - Future Plan

1. Enhanced data storage

   - Create SlackMessage table to store individual message content, timestamps, and metadata instead of only aggregated counts
   - Create SlackReaction table to track all message reactions (emojis, likes) with user and timestamp information
   - Create SlackFile table to store file paths and metadata for files shared in Slack channels

2. Event tracking system

   - Implement Slack event logic to record message lifecycle events: message adding, message editing, message deletion
   - Track reaction events: reaction adding and reaction removing with timestamps
   - Track user events: user joining channels, user leaving channels, user profile updates
   - Store all events with timestamps and user information for comprehensive activity tracking

   Note: This event tracking system will be used to implement a chatbot in Slack channels that can respond to messages, track conversations, and provide automated assistance based on stored message history and user activity.

3. Integration with contribution system

   - Connect SlackUser accounts to the Email/Identity models in the contribution system
   - Link Slack activity to overall contributor profiles so Slack contributions can be tracked alongside GitHub contributions
   - Enable unified reporting that shows all contribution types (commits, PRs, issues, Slack messages) for each contributor identity
