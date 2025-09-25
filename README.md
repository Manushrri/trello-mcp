# Trello MCP Server

A comprehensive Model Context Protocol (MCP) server that provides extensive Trello integration capabilities. This server offers 100+ tools for complete Trello management, enabling seamless card operations, board management, action tracking, and workflow automation through a standardized MCP interface.

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

### ⏱️ Due Dates & Time Management
- **Due Date Management** - Set and update card due dates
- **Time Tracking** - Handle card completion status
- **Deadline Management** - Manage card deadlines and reminders

### 🎨 Customization & Preferences
- **Board Preferences** - Manage board settings and preferences
- **Member Preferences** - Handle user preferences
- **Custom Fields** - Work with custom card fields

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

## Available Tools (100+ Tools)

### 🔧 Card Operations
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

### 📋 Board Management
- `TRELLO_BOARD_CREATE_BOARD` - Create new boards
- `TRELLO_BOARD_FILTER_CARDS_BY_ID_BOARD` - Filter cards on boards
- `TRELLO_BOARD_GET_LISTS_BY_ID_BOARD` - Get board lists
- `TRELLO_GET_BOARDS_CARDS_BY_ID_BOARD` - Get board cards

### 📊 List Management
- `TRELLO_ADD_LISTS` - Create lists with advanced options
- `TRELLO_ADD_LISTS_ARCHIVE_ALL_CARDS_BY_ID_LIST` - Archive all cards in a list
- `TRELLO_ADD_LISTS_CARDS_BY_ID_LIST` - Add cards to lists
- `TRELLO_ADD_LISTS_MOVE_ALL_CARDS_BY_ID_LIST` - Move all cards from list to board

### ✅ Checklist Management
- `TRELLO_ADD_CHECKLISTS` - Create checklists on cards or boards
- `TRELLO_ADD_CHECKLISTS_CHECK_ITEMS_BY_ID_CHECKLIST` - Add items to checklists

### 🏷️ Label Management
- `TRELLO_ADD_LABELS` - Create labels on boards

### 👥 Member Management
- `TRELLO_ADD_MEMBERS_AVATAR_BY_ID_MEMBER` - Upload member avatars
- `TRELLO_ADD_MEMBERS_BOARD_STARS_BY_ID_MEMBER` - Star boards for members
- `TRELLO_ADD_MEMBERS_SAVED_SEARCHES_BY_ID_MEMBER` - Create saved searches

### 🔔 Notifications & Webhooks
- `TRELLO_ADD_NOTIFICATIONS_ALL_READ` - Mark all notifications as read
- `TRELLO_ADD_TOKENS_WEBHOOKS_BY_TOKEN` - Create webhooks

### 🏢 Organization Management
- `TRELLO_ADD_ORGANIZATIONS` - Create new organizations

### 🔄 Session Management
- `TRELLO_ADD_SESSIONS` - Create/update user sessions

### 🎯 Action Analysis & Tracking
- `TRELLO_GET_ACTIONS_BOARD_BY_ID_ACTION` - Get board from action
- `TRELLO_GET_ACTIONS_BOARD_BY_ID_ACTION_BY_FIELD` - Get board field from action
- `TRELLO_GET_ACTIONS_BY_ID_ACTION` - Get action details
- `TRELLO_GET_ACTIONS_BY_ID_ACTION_BY_FIELD` - Get action field (supports "all")
- `TRELLO_GET_ACTIONS_CARD_BY_ID_ACTION` - Get card from action
- `TRELLO_GET_ACTIONS_CARD_BY_ID_ACTION_BY_FIELD` - Get card field from action
- `TRELLO_GET_ACTIONS_DISPLAY_BY_ID_ACTION` - Get action display representation
- `TRELLO_GET_ACTIONS_ENTITIES_BY_ID_ACTION` - Get all entities from action
- `TRELLO_GET_ACTIONS_LIST_BY_ID_ACTION` - Get list from action
- `TRELLO_GET_ACTIONS_LIST_BY_ID_ACTION_BY_FIELD` - Get list field from action
- `TRELLO_GET_ACTIONS_MEMBER_BY_ID_ACTION` - Get member from action
- `TRELLO_GET_ACTIONS_MEMBER_BY_ID_ACTION_BY_FIELD` - Get member field from action
- `TRELLO_GET_ACTIONS_MEMBER_CREATOR_BY_ID_ACTION` - Get member creator from action

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

### 🚀 New Features Added
- **Complete Action Analysis**: 15+ tools for comprehensive action tracking
- **Field-Level Access**: Get specific fields or all data with "all" parameter
- **Advanced Checklist Management**: Create, copy, and manage checklists
- **Enhanced Member Operations**: Avatar uploads, board starring, saved searches
- **Organization Management**: Create and manage Trello organizations
- **Webhook Support**: Set up real-time notifications
- **Session Management**: User session handling
- **Sticker Support**: Add stickers to cards with positioning

### 🔧 Technical Improvements
- **Better Error Handling**: Clear, actionable error messages
- **Parameter Validation**: Comprehensive input validation
- **API Optimization**: Efficient data retrieval and processing
- **Flexible Tool Design**: Support for multiple parameter combinations
- **Deprecated API Handling**: Graceful handling of non-functional endpoints

### 📊 Tool Categories
- **Card Operations**: 12 tools for complete card management
- **Board Management**: 4 tools for board operations
- **List Management**: 4 tools for list operations
- **Checklist Management**: 2 tools for checklist operations
- **Label Management**: 1 tool for label operations
- **Member Management**: 3 tools for member operations
- **Action Analysis**: 15 tools for action tracking and analysis
- **Organization Management**: 1 tool for organization operations
- **Notification Management**: 2 tools for notifications and webhooks
- **Session Management**: 1 tool for session operations

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
jira-mcp/
├── jira_mcp/
│   ├── __init__.py
│   └── mcp_server.py      # Main MCP server implementation
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── .env                  # Environment variables (create this)
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
