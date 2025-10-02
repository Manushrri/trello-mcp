# Trello MCP Server

A comprehensive Model Context Protocol (MCP) server that provides extensive Trello integration capabilities. This server offers **317 tools** for complete Trello management, enabling seamless card operations, board management, action tracking, workflow automation, comprehensive board preference management, and advanced notification processing through a standardized MCP interface.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your Trello API credentials

# Run the server
uv run python trello_mcp/mcp_server.py
```

## Features

### 🔧 Card Management
- **Create Cards** - Create single or bulk cards with full field support
- **Edit Cards** - Update card fields with detailed change tracking
- **Delete Cards** - Remove cards with proper cleanup
- **Get Card Details** - Retrieve comprehensive card information with field-level access
- **Search Cards** - Advanced card searching and filtering
- **Card Movement** - Move cards between lists and boards
- **Card Positioning** - Update card positions within lists

### 👥 Member & Assignment Operations
- **Assign Cards** - Assign cards to members with email/name lookup
- **Find Members** - Search for board members by email, display name, or username
- **Member Management** - Get current user info and all board members
- **Member Actions** - Track member activity and actions
- **Member Profiles** - Retrieve detailed member information

### 💬 Comments & Communication
- **Add Comments** - Add comments to cards
- **Update Comments** - Modify existing comments
- **Delete Comments** - Remove comments with context
- **List Comments** - Retrieve card comment history
- **Comment Management** - Full comment lifecycle management

### 🔗 Card Relationships & Attachments
- **Attach Cards** - Attach URLs and files to cards
- **Card Attachments** - Manage card attachments and links
- **Link Management** - Create relationships between cards
- **Sticker Management** - Add stickers to cards with positioning

### 📋 Board Management
- **Board Operations** - Create and manage Trello boards
- **Board Details** - Get comprehensive board information
- **Board Lists** - Manage board lists and organization
- **Board Members** - Handle board membership and permissions
- **Board Filtering** - Filter cards and content by various criteria

### 📊 List Management
- **List Operations** - Create, update, and delete board lists
- **List Cards** - Manage cards within lists
- **List Movement** - Move cards between lists
- **List Archiving** - Archive and restore lists
- **List Organization** - Handle list positioning and structure

### 🏷️ Label Management
- **Create Labels** - Create board labels with custom colors
- **Label Assignment** - Assign labels to cards
- **Label Management** - Update and delete labels
- **Label Organization** - Organize labels by color and name

### ✅ Checklist Management
- **Create Checklists** - Add checklists to cards or boards
- **Board Checklist Creation** - Create checklists on boards by first creating a card
- **Checklist Items** - Add and manage checklist items
- **Checklist Operations** - Copy, move, and organize checklists
- **Item Conversion** - Convert checklist items to cards

### 🎯 Action Tracking & Analysis
- **Action Details** - Get comprehensive action information
- **Action Fields** - Retrieve specific action fields
- **Action Display** - Get user-friendly action representations
- **Action Entities** - Track all entities involved in actions
- **Action Members** - Get member information from actions
- **Action Cards** - Retrieve cards associated with actions
- **Action Lists** - Get lists involved in actions
- **Action Boards** - Track boards affected by actions

### 🔍 Advanced Search & Filtering
- **Card Filtering** - Advanced card search and filtering
- **Board Filtering** - Filter board content by various criteria
- **Action Filtering** - Search and filter actions
- **Member Filtering** - Find and filter members

### 📈 Organization Management
- **Organization Creation** - Create new Trello organizations
- **Organization Settings** - Manage organization preferences
- **Member Management** - Handle organization membership

### 🔔 Notifications & Webhooks
- **Notification Management** - Mark notifications as read
- **Webhook Creation** - Set up webhooks for real-time updates
- **Activity Tracking** - Monitor system activity
- **Notification Details** - Get comprehensive notification information
- **Notification Entities** - Retrieve entities (boards, cards, lists, members) linked to notifications
- **Notification Members** - Get member information from notifications
- **Notification Cards** - Retrieve card details from notifications
- **Notification Lists** - Get list information from notifications
- **Notification Boards** - Retrieve board details from notifications
- **Notification Organizations** - Get organization information from notifications

### ⏱️ Due Dates & Time Management
- **Due Date Management** - Set and update card due dates
- **Time Tracking** - Handle card completion status
- **Deadline Management** - Manage card deadlines and reminders

### 🎨 Customization & Preferences
- **Board Preferences** - Comprehensive board settings and preferences management
- **Board Permission Control** - Manage board access levels (private, org, public)
- **Comment Permissions** - Control who can comment on cards
- **Voting Permissions** - Manage who can vote on cards
- **Invitation Control** - Control who can invite new members
- **Self-Join Settings** - Allow or require invitations for board access
- **Calendar Integration** - Enable/disable calendar feeds for due dates
- **Card Aging** - Set visual aging effects (pirate/regular mode)
- **Card Covers** - Control card cover visibility
- **Background Settings** - Customize board backgrounds
- **Sidebar Preferences** - Control sidebar visibility and components
- **Member Preferences** - Handle user preferences
- **Custom Fields** - Work with custom card fields

### 🔔 Advanced Notification Processing
- **Notification Analysis** - Comprehensive notification data retrieval and analysis
- **Entity Extraction** - Extract cards, boards, lists, and members from notifications
- **Smart Error Handling** - Intelligent error messages with guidance for different notification types
- **Field-Level Access** - Get specific fields or complete data from notification entities
- **Cross-Entity Relationships** - Understand how notifications connect to different Trello entities

## Installation

### Prerequisites
- Python 3.8 or higher
- Trello account with API access
- Trello API key and token

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd trello-mcp
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Create a `.env` file in the project root:
   ```env
   TRELLO_API_KEY=your_trello_api_key
   TRELLO_API_TOKEN=your_trello_api_token
   BASE_PATH=/path/to/attachments
   ```

4. **Get your Trello API credentials**
   - Go to [Trello API Keys](https://trello.com/app-key)
   - Copy your API Key and use it as `TRELLO_API_KEY`
   - Generate a token by visiting: `https://trello.com/1/authorize?expiration=never&scope=read,write&response_type=token&name=Trello%20MCP%20Server&key=YOUR_API_KEY`
   - Replace `YOUR_API_KEY` with your actual API key
   - Use the generated token as `TRELLO_API_TOKEN`

## Usage

### Starting the Server

```bash
python trello_mcp/mcp_server.py
```

### MCP Client Integration

The server provides tools that can be used by MCP-compatible clients. All tools return meaningful, structured responses instead of empty JSON objects.

### Example Tool Usage

#### Create a Card
```json
{
  "tool": "TRELLO_CREATE_CARD",
  "parameters": {
    "list_id": "64a1b2c3d4e5f6789012345",
    "name": "Fix login bug",
    "description": "Users cannot log in with special characters",
    "due_date": "2024-01-15T23:59:59.000Z",
    "id_members": ["64a1b2c3d4e5f6789012346"]
  }
}
```

#### Add a Comment
```json
{
  "tool": "TRELLO_ADD_COMMENT",
  "parameters": {
    "card_id": "64a1b2c3d4e5f6789012347",
    "comment": "Working on this issue now"
  }
}
```

#### Create a Board
```json
{
  "tool": "TRELLO_CREATE_BOARD",
  "parameters": {
    "name": "Project Management",
    "description": "Main project board",
    "prefs_permission_level": "private"
  }
}
```

#### Update Board Preferences
```json
{
  "tool": "TRELLO_UPDATE_BOARDS_PREFS_BACKGROUND_BY_ID_BOARD",
  "parameters": {
    "id_board": "64a1b2c3d4e5f6789012345",
    "value": "blue"
  }
}
```

#### Set Board Permissions
```json
{
  "tool": "TRELLO_UPDATE_BOARDS_PREFS_PERMISSION_LEVEL_BY_ID_BOARD",
  "parameters": {
    "id_board": "64a1b2c3d4e5f6789012345",
    "value": "private"
  }
}
```

#### Update Label Names
```json
{
  "tool": "TRELLO_UPDATE_BOARDS_LABEL_NAMES_BLUE_BY_ID_BOARD",
  "parameters": {
    "id_board": "64a1b2c3d4e5f6789012345",
    "value": "High Priority"
  }
}
```

#### Create Checklist on Board
```json
{
  "tool": "TRELLO_ADD_BOARDS_CHECKLISTS_BY_ID_BOARD",
  "parameters": {
    "id_board": "64a1b2c3d4e5f6789012345",
    "name": "Project Tasks"
  }
}
```

## Available Tools (317 Tools - Fully Implemented)

### 🔧 Card Operations (26 tools)
- `TRELLO_GET_CARDS_BY_ID_CARD` - Get card by ID with full details
- `TRELLO_GET_CARDS_BY_ID_CARD_BY_FIELD` - Get specific card field
- `TRELLO_GET_CARDS_ACTIONS_BY_ID_CARD` - Get card action history
- `TRELLO_GET_CARDS_ATTACHMENTS_BY_ID_CARD` - Get card attachments
- `TRELLO_GET_CARDS_BOARD_BY_ID_CARD` - Get board for a card
- `TRELLO_GET_CARDS_BOARD_BY_ID_CARD_BY_FIELD` - Get board field for a card
- `TRELLO_GET_CARDS_CHECK_ITEM_STATES_BY_ID_CARD` - Get checklist item states
- `TRELLO_GET_CARDS_CHECKLISTS_BY_ID_CARD` - Get card checklists
- `TRELLO_GET_CARDS_LIST_BY_ID_CARD` - Get list for a card
- `TRELLO_GET_CARDS_LIST_BY_ID_CARD_BY_FIELD` - Get list field for a card
- `TRELLO_GET_CARDS_MEMBERS_BY_ID_CARD` - Get card members
- `TRELLO_GET_CARDS_MEMBERS_VOTED_BY_ID_CARD` - Get members who voted
- `TRELLO_GET_CARDS_STICKERS_BY_ID_CARD` - Get card stickers
- `TRELLO_GET_CARDS_STICKERS_BY_ID_CARD_BY_ID_STICKER` - Get specific sticker

### 📋 Board Management (20+ tools)
- `TRELLO_GET_BOARDS_BY_ID_BOARD` - Get board by ID
- `TRELLO_GET_BOARDS_BY_ID_BOARD_BY_FIELD` - Get specific board field
- `TRELLO_GET_BOARDS_CARDS_BY_ID_BOARD` - Get all board cards
- `TRELLO_GET_BOARDS_CARDS_BY_ID_BOARD_BY_FILTER` - Filter board cards
- `TRELLO_GET_BOARDS_CARDS_BY_ID_BOARD_BY_ID_CARD` - Get specific card from board
- `TRELLO_GET_BOARDS_CHECKLISTS_BY_ID_BOARD` - Get board checklists
- `TRELLO_GET_BOARDS_LABELS_BY_ID_BOARD` - Get board labels
- `TRELLO_GET_BOARDS_LABELS_BY_ID_BOARD_BY_ID_LABEL` - Get specific board label
- `TRELLO_GET_BOARDS_LISTS_BY_ID_BOARD` - Get board lists
- `TRELLO_GET_BOARDS_LISTS_BY_ID_BOARD_BY_FILTER` - Filter board lists
- `TRELLO_GET_BOARDS_MEMBERS_BY_ID_BOARD` - Get board members
- `TRELLO_GET_BOARDS_MEMBERS_BY_ID_BOARD_BY_FILTER` - Filter board members
- `TRELLO_GET_BOARDS_MEMBERS_CARDS_BY_ID_BOARD_BY_ID_MEMBER` - Get member's cards
- `TRELLO_GET_BOARDS_MEMBERSHIPS_BY_ID_BOARD` - Get board memberships
- `TRELLO_GET_BOARDS_MEMBERSHIPS_BY_ID_BOARD_BY_ID_MEMBERSHIP` - Get specific membership
- `TRELLO_GET_BOARDS_MEMBERS_INVITED_BY_ID_BOARD` - Get invited members
- `TRELLO_GET_BOARDS_MEMBERS_INVITED_BY_ID_BOARD_BY_FIELD` - Get invited member field
- `TRELLO_GET_BOARDS_MY_PREFS_BY_ID_BOARD` - Get user's board preferences
- `TRELLO_GET_BOARDS_ORGANIZATION_BY_ID_BOARD` - Get board organization
- `TRELLO_GET_BOARDS_ORGANIZATION_BY_ID_BOARD_BY_FIELD` - Get organization field

### 📊 List Management (15+ tools)
- `TRELLO_GET_LISTS_BY_ID_LIST` - Get list by ID
- `TRELLO_GET_LISTS_BY_ID_LIST_BY_FIELD` - Get specific list field
- `TRELLO_GET_LISTS_ACTIONS_BY_ID_LIST` - Get list action history
- `TRELLO_GET_LISTS_BOARD_BY_ID_LIST` - Get board for a list
- `TRELLO_GET_LISTS_BOARD_BY_ID_LIST_BY_FIELD` - Get board field for a list
- `TRELLO_GET_LISTS_CARDS_BY_ID_LIST` - Get list cards
- `TRELLO_GET_LISTS_CARDS_BY_ID_LIST_BY_FILTER` - Filter list cards

### ✅ Checklist Management (10+ tools)
- `TRELLO_GET_CHECKLISTS_BY_ID_CHECKLIST` - Get checklist by ID
- `TRELLO_GET_CHECKLISTS_BY_ID_CHECKLIST_BY_FIELD` - Get checklist field
- `TRELLO_GET_CHECKLISTS_BOARD_BY_ID_CHECKLIST` - Get board for checklist
- `TRELLO_GET_CHECKLISTS_BOARD_BY_ID_CHECKLIST_BY_FIELD` - Get board field
- `TRELLO_GET_CHECKLISTS_CARDS_BY_ID_CHECKLIST` - Get cards in checklist
- `TRELLO_GET_CHECKLISTS_CARDS_BY_ID_CHECKLIST_BY_FILTER` - Filter checklist cards
- `TRELLO_GET_CHECKLISTS_CHECK_ITEMS_BY_ID_CHECKLIST` - Get checklist items
- `TRELLO_GET_CHECK_ITEM_BY_ID` - Get specific checklist item

### 🏷️ Label Management (5+ tools)
- `TRELLO_GET_LABELS_BY_ID_LABEL` - Get label by ID
- `TRELLO_GET_LABELS_BOARD_BY_ID_LABEL` - Get board for label
- `TRELLO_GET_LABELS_BOARD_BY_ID_LABEL_BY_FIELD` - Get board field for label

### 🎯 Action Analysis (20+ tools)
- `TRELLO_GET_ACTIONS_BY_ID_ACTION` - Get action details
- `TRELLO_GET_ACTIONS_BY_ID_ACTION_BY_FIELD` - Get action field
- `TRELLO_GET_ACTIONS_BOARD_BY_ID_ACTION` - Get board from action
- `TRELLO_GET_ACTIONS_BOARD_BY_ID_ACTION_BY_FIELD` - Get board field from action
- `TRELLO_GET_ACTIONS_CARD_BY_ID_ACTION` - Get card from action
- `TRELLO_GET_ACTIONS_CARD_BY_ID_ACTION_BY_FIELD` - Get card field from action
- `TRELLO_GET_ACTIONS_DISPLAY_BY_ID_ACTION` - Get action display
- `TRELLO_GET_ACTIONS_ENTITIES_BY_ID_ACTION` - Get action entities
- `TRELLO_GET_ACTIONS_LIST_BY_ID_ACTION` - Get list from action
- `TRELLO_GET_ACTIONS_LIST_BY_ID_ACTION_BY_FIELD` - Get list field from action
- `TRELLO_GET_ACTIONS_MEMBER_BY_ID_ACTION` - Get member from action
- `TRELLO_GET_ACTIONS_MEMBER_BY_ID_ACTION_BY_FIELD` - Get member field from action
- `TRELLO_GET_ACTIONS_MEMBER_CREATOR_BY_ID_ACTION` - Get action creator
- `TRELLO_GET_ACTIONS_MEMBER_CREATOR_BY_ID_ACTION_BY_FIELD` - Get creator field
- `TRELLO_GET_ACTIONS_ORGANIZATION_BY_ID_ACTION` - Get organization from action
- `TRELLO_GET_ACTIONS_ORGANIZATION_BY_ID_ACTION_BY_FIELD` - Get org field from action

### 🔧 Card Operations (Legacy Tools)
- `TRELLO_GET_BOARDS_CARDS_BY_ID_BOARD` - Get all cards from a board
- `TRELLO_ADD_CARDS_ACTIONS_COMMENTS_BY_ID_CARD` - Add comments to cards
- `TRELLO_ADD_CARDS_CHECKLIST_CHECK_ITEM_BY_ID_CARD_BY_ID_CHECKLIST` - Add check items to checklists
- `TRELLO_ADD_CARDS_CHECKLISTS_BY_ID_CARD` - Add checklists to cards
- `TRELLO_ADD_CARDS_ID_LABELS_BY_ID_CARD` - Add existing labels to cards
- `TRELLO_ADD_CARDS_ID_MEMBERS_BY_ID_CARD` - Assign members to cards
- `TRELLO_ADD_CARDS_LABELS_BY_ID_CARD` - Add labels to cards by name/color
- `TRELLO_ADD_CARDS_STICKERS_BY_ID_CARD` - Add stickers to cards
- `TRELLO_CARD_GET_BY_ID_FIELD` - Get specific card fields (supports "all")
- `TRELLO_CARD_UPDATE_ID_LIST_BY_ID_CARD` - Move cards between lists
- `TRELLO_CARD_UPDATE_POS_BY_ID_CARD` - Update card positions
- `TRELLO_CONVERT_CHECKLIST_ITEM_TO_CARD` - Convert checklist items to cards

### 📋 Board Management (48 tools)
- `TRELLO_BOARD_CREATE_BOARD` - Create new boards
- `TRELLO_BOARD_FILTER_CARDS_BY_ID_BOARD` - Filter cards on boards
- `TRELLO_BOARD_GET_LISTS_BY_ID_BOARD` - Get board lists
- `TRELLO_GET_BOARDS_CARDS_BY_ID_BOARD` - Get board cards

### 📊 List Management (Legacy Tools)
- `TRELLO_ADD_LISTS` - Create lists with advanced options
- `TRELLO_ADD_LISTS_ARCHIVE_ALL_CARDS_BY_ID_LIST` - Archive all cards in a list
- `TRELLO_ADD_LISTS_CARDS_BY_ID_LIST` - Add cards to lists
- `TRELLO_ADD_LISTS_MOVE_ALL_CARDS_BY_ID_LIST` - Move all cards from list to board

### ✅ Checklist Management (Legacy Tools)
- `TRELLO_ADD_CHECKLISTS` - Create checklists on cards or boards
- `TRELLO_ADD_BOARDS_CHECKLISTS_BY_ID_BOARD` - Create checklists on boards (creates card first)
- `TRELLO_ADD_CHECKLISTS_CHECK_ITEMS_BY_ID_CHECKLIST` - Add items to checklists

### 🏷️ Label Management (Legacy Tools)
- `TRELLO_ADD_LABELS` - Create labels on boards

### 👥 Member Management (Legacy Tools)
- `TRELLO_ADD_MEMBERS_AVATAR_BY_ID_MEMBER` - Upload member avatars
- `TRELLO_ADD_MEMBERS_BOARD_STARS_BY_ID_MEMBER` - Star boards for members
- `TRELLO_ADD_MEMBERS_SAVED_SEARCHES_BY_ID_MEMBER` - Create saved searches
- `TRELLO_UPDATE_MEMBERS_AVATAR_SOURCE_BY_ID_MEMBER` - Update member avatar source
- `TRELLO_UPDATE_MEMBER_SAVED_SEARCH` - Update member saved search
- `TRELLO_UPDATE_MEMBER_SAVED_SEARCH_NAME` - Update member saved search name
- `TRELLO_UPDATE_MEMBER_SAVED_SEARCH_POS` - Update member saved search position
- `TRELLO_UPDATE_MEMBER_SAVED_SEARCH_QUERY` - Update member saved search query
- `TRELLO_UPDATE_MEMBERS_BIO_BY_ID_MEMBER` - Update member bio

### 🔔 Notifications & Webhooks (Legacy Tools)
- `TRELLO_ADD_NOTIFICATIONS_ALL_READ` - Mark all notifications as read
- `TRELLO_ADD_TOKENS_WEBHOOKS_BY_TOKEN` - Create webhooks

### 🔔 Advanced Notification Tools (33 tools)
- `TRELLO_GET_NOTIFICATIONS_BY_ID_NOTIFICATION` - Get comprehensive notification details
- `TRELLO_GET_NOTIFICATIONS_ENTITIES_BY_ID_NOTIFICATION` - Get entities linked to notifications
- `TRELLO_GET_NOTIFICATIONS_MEMBER_BY_ID_NOTIFICATION_BY_FIELD` - Get specific member field from notification
- `TRELLO_GET_NOTIFICATIONS_MEMBER_CREATOR_BY_ID_NOTIFICATION` - Get notification creator details
- `TRELLO_GET_NOTIFICATIONS_ORGANIZATION_BY_ID_NOTIFICATION` - Get organization from notification
- `TRELLO_GET_NOTIFICATIONS_CARD_BY_ID_NOTIFICATION` - Get card details from notification
- `TRELLO_GET_NOTIFICATIONS_CARD_BY_ID_NOTIFICATION_BY_FIELD` - Get specific card field from notification
- `TRELLO_GET_NOTIFICATIONS_LIST_BY_ID_NOTIFICATION` - Get list details from notification
- `TRELLO_GET_NOTIFICATIONS_LIST_BY_ID_NOTIFICATION_BY_FIELD` - Get specific list field from notification
- `TRELLO_GET_NOTIFICATIONS_BOARD_BY_ID_NOTIFICATION` - Get board details from notification
- `TRELLO_GET_NOTIFICATIONS_BOARD_BY_ID_NOTIFICATION_BY_FIELD` - Get specific board field from notification

### 🏢 Organization Management (Legacy Tools)
- `TRELLO_ADD_ORGANIZATIONS` - Create new organizations

### 🔄 Session Management (Legacy Tools)
- `TRELLO_ADD_SESSIONS` - Create/update user sessions

### 🎨 Board Preference Management (92 tools)
- `TRELLO_UPDATE_BOARDS_BY_ID_BOARD` - Update comprehensive board attributes
- `TRELLO_UPDATE_BOARDS_NAME_BY_ID_BOARD` - Update board name
- `TRELLO_UPDATE_BOARDS_DESC_BY_ID_BOARD` - Update board description
- `TRELLO_UPDATE_BOARDS_CLOSED_BY_ID_BOARD` - Archive/unarchive boards
- `TRELLO_UPDATE_BOARDS_SUBSCRIBED_BY_ID_BOARD` - Update subscription status
- `TRELLO_UPDATE_BOARDS_PREFS_BACKGROUND_BY_ID_BOARD` - Update board background
- `TRELLO_UPDATE_BOARDS_PREFS_CALENDAR_FEED_ENABLED_BY_ID_BOARD` - Enable/disable calendar feeds
- `TRELLO_UPDATE_BOARDS_PREFS_CARD_AGING_BY_ID_BOARD` - Set card aging mode
- `TRELLO_UPDATE_BOARDS_PREFS_CARD_COVERS_BY_ID_BOARD` - Control card cover visibility
- `TRELLO_UPDATE_BOARDS_PREFS_COMMENTS_BY_ID_BOARD` - Set comment permissions
- `TRELLO_UPDATE_BOARDS_PREFS_INVITATIONS_BY_ID_BOARD` - Set invitation permissions
- `TRELLO_UPDATE_BOARDS_PREFS_PERMISSION_LEVEL_BY_ID_BOARD` - Set board access level
- `TRELLO_UPDATE_BOARDS_PREFS_SELF_JOIN_BY_ID_BOARD` - Control self-join settings
- `TRELLO_UPDATE_BOARDS_PREFS_VOTING_BY_ID_BOARD` - Set voting permissions
- `TRELLO_UPDATE_BOARDS_LABEL_NAMES_BLUE_BY_ID_BOARD` - Update blue label name
- `TRELLO_UPDATE_BOARDS_LABEL_NAMES_GREEN_BY_ID_BOARD` - Update green label name
- `TRELLO_UPDATE_BOARDS_LABEL_NAMES_ORANGE_BY_ID_BOARD` - Update orange label name
- `TRELLO_UPDATE_BOARDS_LABEL_NAMES_PURPLE_BY_ID_BOARD` - Update purple label name
- `TRELLO_UPDATE_BOARDS_LABEL_NAMES_RED_BY_ID_BOARD` - Update red label name
- `TRELLO_UPDATE_BOARDS_LABEL_NAMES_YELLOW_BY_ID_BOARD` - Update yellow label name
- `TRELLO_UPDATE_BOARDS_MEMBERS_BY_ID_BOARD` - Add/update board members
- `TRELLO_UPDATE_BOARDS_MEMBERS_BY_ID_BOARD_BY_ID_MEMBER` - Update member attributes
- `TRELLO_UPDATE_BOARDS_ID_ORGANIZATION_BY_ID_BOARD` - Move board to organization
- `TRELLO_UPDATE_BOARDS_MY_PREFS_EMAIL_POSITION_BY_ID_BOARD` - Set email position preference
- `TRELLO_UPDATE_BOARDS_MY_PREFS_ID_EMAIL_LIST_BY_ID_BOARD` - Set email list preference
- `TRELLO_UPDATE_BOARDS_MY_PREFS_SHOW_LIST_GUIDE_BY_ID_BOARD` - Set list guide preference
- `TRELLO_UPDATE_BOARDS_MY_PREFS_SHOW_SIDEBAR_ACTIVITY_BY_ID_BOARD` - Set sidebar activity preference
- `TRELLO_UPDATE_BOARDS_MY_PREFS_SHOW_SIDEBAR_BY_ID_BOARD` - Set sidebar visibility
- `TRELLO_UPDATE_BOARDS_MY_PREFS_SHOW_SIDEBAR_MEMBERS_BY_ID_BOARD` - Set sidebar members preference

### 🔧 Deprecated Tools (Legacy Support)
- `TRELLO_LIST_CREATE_LIST` - Create lists (deprecated wrapper)
- `TRELLO_LIST_GET_BY_ID_LIST` - Get list by ID (deprecated wrapper)
- `TRELLO_LIST_ID_BOARD_GET` - Get board by list ID (deprecated wrapper)
- `TRELLO_MEMBER_GET_BOARDS` - Get member boards (deprecated wrapper)
- `TRELLO_MEMBER_GET_BOARDS_BY_ID_MEMBER` - Get member boards by ID (deprecated wrapper)
- `TRELLO_TOKEN_GET_MEMBER_BY_TOKEN` - Get token member (deprecated wrapper)

### 🔍 Advanced Features
- **Field-Level Access**: Most tools support "all" as a field value to get complete data
- **Flexible Parameters**: Tools support multiple parameter combinations
- **Error Handling**: Comprehensive error messages and validation
- **Optimized Queries**: Field-specific tools for efficient data retrieval
- **Action Context**: Complete action analysis and tracking capabilities
- **Multi-Step Operations**: Complex operations like moving all cards between boards
- **Simulated APIs**: Fallback implementations for deprecated Trello endpoints
- **Comprehensive Coverage**: 100+ tools covering all major Trello functionality

## Recent Updates & Improvements

### 🚀 Current Implementation Status
- **317 Tools Implemented**: Complete Trello integration with comprehensive coverage
- **Comprehensive GET Operations**: 80+ tools for detailed data retrieval
- **Board Preference Management**: 50+ tools for complete board customization
- **Field-Level Access**: Get specific fields or all data with "all" parameter
- **Card Relationship Tools**: Get board, list, members, stickers, and attachments for cards
- **Board Management Tools**: Get members, organization, preferences, and detailed board info
- **List Management Tools**: Get actions, board info, and cards for lists
- **Checklist Management Tools**: Get board info, cards, and check items for checklists
- **Label Management Tools**: Get board info and detailed label information
- **Action Analysis Tools**: 20+ tools for comprehensive action tracking and analysis
- **Board Customization Tools**: Complete control over board appearance and behavior
- **Permission Management**: Granular control over board access and member permissions
- **Enhanced Error Handling**: Better error messages and API limitation documentation

### 🔧 Technical Improvements
- **Better Error Handling**: Clear, actionable error messages with API limitation notes
- **Parameter Validation**: Comprehensive input validation with proper type hints
- **API Optimization**: Efficient data retrieval and processing
- **Flexible Tool Design**: Support for multiple parameter combinations
- **Deprecated API Handling**: Graceful handling of non-functional endpoints
- **Type Safety**: Proper type annotations using `str | None` for optional parameters
- **Smart API Workarounds**: Tools like `TRELLO_ADD_BOARDS_CHECKLISTS_BY_ID_BOARD` handle Trello API limitations by creating cards first

### 📊 Tool Categories (Updated)
- **Card Operations**: 26 tools for complete card management and relationships
- **Board Management**: 48 tools for board operations and detailed info
- **Board Preference Management**: 92 tools for comprehensive board customization
- **List Management**: ~15 tools for list operations and relationships
- **Checklist Management**: ~10 tools for checklist operations and relationships
- **Label Management**: ~5 tools for label operations and relationships
- **Action Analysis**: ~20 tools for action tracking and analysis
- **Member Management**: ~10 tools for member operations
- **Notifications**: 33 tools for comprehensive notification management
- **Organization Management**: ~5 tools for organization operations
- **Session Management**: ~2 tools for session management
- **Advanced Features**: ~5 tools for batch operations and search
- **Deprecated Tools**: ~10 tools with legacy support and deprecation notices
- **Total Tools**: 317 comprehensive Trello integration tools

## Response Format

All tools now return meaningful, structured responses instead of empty JSON objects. Example:

```json
{
  "success": true,
  "action": "card_created",
  "card_id": "64a1b2c3d4e5f6789012347",
  "card_name": "Fix login bug",
  "list_name": "To Do",
  "due_date": "2024-01-15T23:59:59.000Z",
  "members": ["John Doe"],
  "message": "Card 'Fix login bug' has been successfully created in list 'To Do'"
}
```

## 🔔 Advanced Notification Management

The Trello MCP Server includes comprehensive notification management tools that allow you to retrieve detailed information from Trello notifications and their associated entities.

### Notification Tool Categories

#### 📋 **Core Notification Tools**
- **`TRELLO_GET_NOTIFICATIONS_BY_ID_NOTIFICATION`** - Get complete notification details
- **`TRELLO_GET_NOTIFICATIONS_ENTITIES_BY_ID_NOTIFICATION`** - Get all entities linked to a notification

#### 👥 **Member-Related Tools**
- **`TRELLO_GET_NOTIFICATIONS_MEMBER_BY_ID_NOTIFICATION_BY_FIELD`** - Get specific member field from notification
- **`TRELLO_GET_NOTIFICATIONS_MEMBER_CREATOR_BY_ID_NOTIFICATION`** - Get notification creator details

#### 🃏 **Card-Related Tools**
- **`TRELLO_GET_NOTIFICATIONS_CARD_BY_ID_NOTIFICATION`** - Get complete card details from notification
- **`TRELLO_GET_NOTIFICATIONS_CARD_BY_ID_NOTIFICATION_BY_FIELD`** - Get specific card field from notification

#### 📋 **List-Related Tools**
- **`TRELLO_GET_NOTIFICATIONS_LIST_BY_ID_NOTIFICATION`** - Get list details from notification
- **`TRELLO_GET_NOTIFICATIONS_LIST_BY_ID_NOTIFICATION_BY_FIELD`** - Get specific list field from notification

#### 📌 **Board-Related Tools**
- **`TRELLO_GET_NOTIFICATIONS_BOARD_BY_ID_NOTIFICATION`** - Get board details from notification
- **`TRELLO_GET_NOTIFICATIONS_BOARD_BY_ID_NOTIFICATION_BY_FIELD`** - Get specific board field from notification

#### 🏢 **Organization Tools**
- **`TRELLO_GET_NOTIFICATIONS_ORGANIZATION_BY_ID_NOTIFICATION`** - Get organization details from notification

### Usage Examples

#### Get Card Details from Notification
```json
{
  "tool": "TRELLO_GET_NOTIFICATIONS_CARD_BY_ID_NOTIFICATION",
  "parameters": {
    "id_notification": "68dc97cade43cb4b1be9cd63",
    "fields": "all"
  }
}
```

#### Get Specific Card Field
```json
{
  "tool": "TRELLO_GET_NOTIFICATIONS_CARD_BY_ID_NOTIFICATION_BY_FIELD",
  "parameters": {
    "id_notification": "68dc97cade43cb4b1be9cd63",
    "field": "name"
  }
}
```

#### Get All Entities from Notification
```json
{
  "tool": "TRELLO_GET_NOTIFICATIONS_ENTITIES_BY_ID_NOTIFICATION",
  "parameters": {
    "id_notification": "68dc97cade43cb4b1be9cd63"
  }
}
```

### Notification Types and Compatibility

| Notification Type | Card Tools | List Tools | Board Tools | Member Tools |
|------------------|------------|------------|-------------|--------------|
| `mentionedOnCard` | ✅ Works | ❌ No list | ✅ Works | ✅ Works |
| `addedToCard` | ✅ Works | ❌ No list | ✅ Works | ✅ Works |
| `memberJoinedWorkspace` | ❌ No card | ❌ No list | ❌ No board | ✅ Works |
| `commentCard` | ✅ Works | ❌ No list | ✅ Works | ✅ Works |
| `updateCard` | ✅ Works | ❌ No list | ✅ Works | ✅ Works |

### Error Handling

All notification tools include comprehensive error handling:
- **404 "model not found"** - Notification doesn't have the requested entity type
- **Clear guidance** - Explains why the operation failed
- **Helpful suggestions** - Recommends alternative approaches
- **Educational content** - Explains Trello's notification structure

### Working Notification IDs

For testing, use these notification IDs that have associated entities:
- **`68dc97cade43cb4b1be9cd63`** - `mentionedOnCard` (has card and board)
- **`68dc949e2813485ee5558b8a`** - `addedToCard` (has card and board)

## Configuration

### Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `TRELLO_API_KEY` | Yes | Your Trello API key | `abc123def456...` |
| `TRELLO_API_TOKEN` | Yes | Your Trello API token | `xyz789uvw012...` |
| `BASE_PATH` | No | Base path for file attachments | `/path/to/files` |

### Trello API Setup

1. Go to [Trello API Keys](https://trello.com/app-key)
2. Copy your API Key and use it as `TRELLO_API_KEY`
3. Generate a token by visiting: `https://trello.com/1/authorize?expiration=never&scope=read,write&response_type=token&name=Trello%20MCP%20Server&key=YOUR_API_KEY`
4. Replace `YOUR_API_KEY` with your actual API key
5. Use the generated token as `TRELLO_API_TOKEN`

## Development

### Running Tests

```bash
pytest
```

### Code Structure

```
trello-mcp/
├── trello_mcp/
│   ├── __init__.py
│   └── mcp_server.py      # Main MCP server implementation
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── .env                  # Environment variables (create this)
```

### Code Quality

```bash
# Format code
black trello_mcp/

# Lint code
flake8 trello_mcp/

# Type checking
mypy trello_mcp/
```

### Adding New Tools

1. Add the tool function with `@mcp.tool` decorator
2. Include meaningful response data instead of raw API responses
3. Add proper error handling and validation
4. Update this README with the new tool

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Verify your Trello API key and token are correct
   - Check that your API token has the necessary permissions
   - Ensure your Trello account is active

2. **Permission Errors**
   - Verify your Trello user has necessary board/card permissions
   - Check board access rights for the operations you're trying to perform
   - Ensure you're a member of boards you're trying to modify

3. **404 Errors**
   - Verify that card, board, list, or action IDs are correct
   - Use `TRELLO_GET_BOARDS_CARDS_BY_ID_BOARD` to get valid card IDs
   - Check that resources haven't been deleted or moved

4. **Field Access Errors**
   - Use "all" as field value to get complete data
   - Check available fields using the "all" option first
   - Verify field names are correct (case-sensitive)

5. **API Limitations**
   - Some endpoints may be deprecated (voting, direct session management)
   - Use alternative approaches for unsupported operations
   - Check Trello API documentation for current endpoint status

### Debug Mode

Use the comprehensive action analysis tools to troubleshoot:

```json
{
  "tool": "TRELLO_GET_ACTIONS_BY_ID_ACTION",
  "parameters": {
    "id_action": "your_action_id"
  }
}
```

### Getting Valid IDs

To get valid resource IDs for testing:

```json
{
  "tool": "TRELLO_GET_BOARDS_CARDS_BY_ID_BOARD",
  "parameters": {
    "id_board": "your_board_id"
  }
}
```

### Field-Level Debugging

To see all available fields:

```json
{
  "tool": "TRELLO_CARD_GET_BY_ID_FIELD",
  "parameters": {
    "id_card": "your_card_id",
    "field": "all"
  }
}
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For issues and questions:
1. Check the troubleshooting section
2. Use the diagnostic tools
3. Create an issue in the repository
4. Provide diagnostic information when reporting issues
