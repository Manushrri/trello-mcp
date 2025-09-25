import os
import requests
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from typing import Optional, List, Dict, Any, Annotated

# Load .env file automatically
load_dotenv()

def get_env(var: str) -> str:
    """Fetch environment variable or raise error if missing."""
    value = os.getenv(var)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {var}")
    return value

def get_trello_base_url() -> str:
    """Build Trello API base URL."""
    # Trello API uses a single base URL for all endpoints
    return "https://api.trello.com/1"

def get_trello_auth_params() -> dict:
    """Get Trello authentication parameters (API key + token)."""
    return {
        "key": get_env("TRELLO_API_KEY"),
        "token": get_env("TRELLO_API_TOKEN")
    }

def get_base_path() -> str:
    """Return the BASE_PATH for file uploads."""
    return get_env("BASE_PATH")

# Initialize MCP server
mcp = FastMCP("trello-mcp")

def trello_request(method: str, endpoint: str, **kwargs):
    """Helper for authenticated Trello API requests."""
    url = f"{get_trello_base_url()}{endpoint}"
    
    # Get authentication parameters
    auth_params = get_trello_auth_params()
    
    # Add auth params to query parameters for GET requests or data for POST/PUT
    if method.upper() == "GET":
        params = kwargs.get("params", {})
        params.update(auth_params)
        kwargs["params"] = params
    else:
        data = kwargs.get("data", {})
        if isinstance(data, dict):
            data.update(auth_params)
        kwargs["data"] = data

    headers = kwargs.pop("headers", {})
    headers["Accept"] = "application/json"

    try:
        response = requests.request(method, url, headers=headers, **kwargs)
        if response.ok:
            try:
                return response.json() if response.text else {}
            except Exception:
                return {"raw": response.text}
        # Non-2xx: raise to surface an MCP error toast
        raise RuntimeError(f"Trello API error {response.status_code}: {response.text}")
    except Exception as e:
        # Bubble up as a tool error
        raise RuntimeError(str(e))

def _validate_required(params: Dict[str, Any], required: List[str]):
    """Raise ValueError if any required params are missing/blank.

    Treats empty strings, None, and empty lists as missing.
    """
    missing = []
    for key in required:
        value = params.get(key)
        if value is None:
            missing.append(key)
        elif isinstance(value, str) and value.strip() == "":
            missing.append(key)
        elif isinstance(value, (list, dict)) and len(value) == 0:
            missing.append(key)
    if missing:
        raise ValueError(f"Missing required parameter(s): {', '.join(missing)}")
    return None

# -------------------- TOOLS --------------------

@mcp.tool(
    "TRELLO_ACTION_GET_BOARD_BY_ID_ACTION",
    description="Get board by action id. Deprecated: use `get actions board by id action` instead. retrieves details for the trello board associated with a specific action id, returning board information only.",
)
def TRELLO_ACTION_GET_BOARD_BY_ID_ACTION(
    id_action: Annotated[str, "The ID of the action to retrieve board information for."],
    fields: Annotated[Optional[str], "Fields to return. Defaults to all."] = "all"
):
    """Get board by action id. Deprecated: use `get actions board by id action` instead. retrieves details for the trello board associated with a specific action id, returning board information only."""
    err = _validate_required({"id_action": id_action}, ["id_action"])
    if err:
        return err
    
    endpoint = f"/actions/{id_action}/board"
    params = {}
    if fields != "all":
        params["fields"] = fields
    
    result = trello_request("GET", endpoint, params=params)
    
    return {
        "successful": True,
        "data": result,
        "action": "get_board_by_action",
        "id_action": id_action,
        "fields": fields,
        "message": f"Successfully retrieved board for action {id_action}"
    }

@mcp.tool(
    "TRELLO_ACTION_GET_BY_ID",
    description="Get action by ID. Deprecated: use `get actions by id action` instead. retrieves detailed information about a specific trello action by its id.",
)
def TRELLO_ACTION_GET_BY_ID(
    id_action: Annotated[str, "The ID of the action to retrieve (required)."],
    display: Annotated[Optional[str], "Display format for the action."] = None,
    entities: Annotated[Optional[str], "Entities to include in the response."] = None,
    fields: Annotated[Optional[str], "Fields to return. Defaults to all."] = "all",
    member: Annotated[Optional[str], "Member information to include."] = None,
    member_creator: Annotated[Optional[str], "Member creator information to include."] = None,
    member_creator_fields: Annotated[Optional[str], "Member creator fields to return. Defaults to avatarHash, fullName, initials and username."] = "avatarHash,fullName,initials,username",
    member_fields: Annotated[Optional[str], "Member fields to return. Defaults to avatarHash, fullName, initials and username."] = "avatarHash,fullName,initials,username"
):
    """Get action by ID. Deprecated: use `get actions by id action` instead. retrieves detailed information about a specific trello action by its id."""
    err = _validate_required({"id_action": id_action}, ["id_action"])
    if err:
        return err
    
    endpoint = f"/actions/{id_action}"
    params = {}
    
    if display:
        params["display"] = display
    if entities:
        params["entities"] = entities
    if fields != "all":
        params["fields"] = fields
    if member:
        params["member"] = member
    if member_creator:
        params["memberCreator"] = member_creator
    if member_creator_fields != "avatarHash,fullName,initials,username":
        params["memberCreator_fields"] = member_creator_fields
    if member_fields != "avatarHash,fullName,initials,username":
        params["member_fields"] = member_fields
    
    result = trello_request("GET", endpoint, params=params)
    
    return {
        "successful": True,
        "data": result,
        "action": "get_action_by_id",
        "id_action": id_action,
        "display": display,
        "entities": entities,
        "fields": fields,
        "member": member,
        "member_creator": member_creator,
        "member_creator_fields": member_creator_fields,
        "member_fields": member_fields,
        "message": f"Successfully retrieved action {id_action}"
        }

@mcp.tool(
    "TRELLO_ACTION_GET_LIST_BY_ID_ACTION",
    description="Get an action's list. Retrieves the trello list associated with a specific trello action id, for actions linked to a list. <<DEPRECATED use get_actions_list_by_id_action>>",
)
def TRELLO_ACTION_GET_LIST_BY_ID_ACTION(
    id_action: Annotated[str, "The ID of the action to retrieve list information for."],
    fields: Annotated[Optional[str], "Fields to return. Defaults to all."] = "all"
):
    """Get an action's list. Retrieves the trello list associated with a specific trello action id, for actions linked to a list. <<DEPRECATED use get_actions_list_by_id_action>>"""
    err = _validate_required({"id_action": id_action}, ["id_action"])
    if err:
        return err
    
    endpoint = f"/actions/{id_action}/list"
    params = {}
    if fields != "all":
        params["fields"] = fields
    
    result = trello_request("GET", endpoint, params=params)
    
    return {
        "successful": True,
        "data": result,
        "action": "get_list_by_action",
        "id_action": id_action,
        "fields": fields,
        "message": f"Successfully retrieved list for action {id_action}"
        }

@mcp.tool(
    "TRELLO_ADD_BOARDS",
    description="Add board. Creates a new trello board; the 'name' parameter is required for creation, and various preferences can be customized or cloned from a source board.",
)
def TRELLO_ADD_BOARDS(
    name: Annotated[str, "The name of the board to create (required)."],
    closed: Annotated[Optional[str], "Whether the board is closed."] = None,
    desc: Annotated[Optional[str], "Description of the board."] = None,
    id_board_source: Annotated[Optional[str], "ID of the board to copy from."] = None,
    id_organization: Annotated[Optional[str], "ID of the organization to add the board to."] = None,
    keep_from_source: Annotated[Optional[str], "What to keep from the source board."] = None,
    label_names_blue: Annotated[Optional[str], "Name for blue label."] = None,
    label_names_green: Annotated[Optional[str], "Name for green label."] = None,
    label_names_orange: Annotated[Optional[str], "Name for orange label."] = None,
    label_names_purple: Annotated[Optional[str], "Name for purple label."] = None,
    label_names_red: Annotated[Optional[str], "Name for red label."] = None,
    label_names_yellow: Annotated[Optional[str], "Name for yellow label."] = None,
    power_ups: Annotated[Optional[str], "Power-ups to enable."] = None,
    prefs_background: Annotated[Optional[str], "Background preference."] = None,
    prefs_calendar_feed_enabled: Annotated[Optional[str], "Whether calendar feed is enabled."] = None,
    prefs_card_aging: Annotated[Optional[str], "Card aging preference."] = None,
    prefs_card_covers: Annotated[Optional[str], "Card covers preference."] = None,
    prefs_comments: Annotated[Optional[str], "Comments preference."] = None,
    prefs_invitations: Annotated[Optional[str], "Invitations preference."] = None,
    prefs_permission_level: Annotated[Optional[str], "Permission level preference."] = None,
    prefs_self_join: Annotated[Optional[str], "Self-join preference."] = None,
    prefs_voting: Annotated[Optional[str], "Voting preference."] = None,
    subscribed: Annotated[Optional[str], "Whether the user is subscribed to the board."] = None
):
    """Add board. Creates a new trello board; the 'name' parameter is required for creation, and various preferences can be customized or cloned from a source board."""
    err = _validate_required({"name": name}, ["name"])
    if err:
        return err
    
    endpoint = "/boards"
    data = {"name": name}
    
    # Add optional parameters if provided
    if closed is not None:
        data["closed"] = closed
    if desc is not None:
        data["desc"] = desc
    if id_board_source is not None:
        data["idBoardSource"] = id_board_source
    if id_organization is not None:
        data["idOrganization"] = id_organization
    if keep_from_source is not None:
        data["keepFromSource"] = keep_from_source
    if label_names_blue is not None:
        data["labelNames/blue"] = label_names_blue
    if label_names_green is not None:
        data["labelNames/green"] = label_names_green
    if label_names_orange is not None:
        data["labelNames/orange"] = label_names_orange
    if label_names_purple is not None:
        data["labelNames/purple"] = label_names_purple
    if label_names_red is not None:
        data["labelNames/red"] = label_names_red
    if label_names_yellow is not None:
        data["labelNames/yellow"] = label_names_yellow
    if power_ups is not None:
        data["powerUps"] = power_ups
    if prefs_background is not None:
        data["prefs/background"] = prefs_background
    if prefs_calendar_feed_enabled is not None:
        data["prefs/calendarFeedEnabled"] = prefs_calendar_feed_enabled
    if prefs_card_aging is not None:
        data["prefs/cardAging"] = prefs_card_aging
    if prefs_card_covers is not None:
        data["prefs/cardCovers"] = prefs_card_covers
    if prefs_comments is not None:
        data["prefs/comments"] = prefs_comments
    if prefs_invitations is not None:
        data["prefs/invitations"] = prefs_invitations
    if prefs_permission_level is not None:
        data["prefs/permissionLevel"] = prefs_permission_level
    if prefs_self_join is not None:
        data["prefs/selfJoin"] = prefs_self_join
    if prefs_voting is not None:
        data["prefs/voting"] = prefs_voting
    if subscribed is not None:
        data["subscribed"] = subscribed
    
    result = trello_request("POST", endpoint, data=data)
    
    return {
        "successful": True,
        "data": result,
        "action": "add_board",
        "board_name": name,
        "message": f"Successfully created board '{name}'"
        }

@mcp.tool(
    "TRELLO_ADD_BOARDS_CALENDAR_KEY_GENERATE_BY_ID_BOARD",
    description="Get board calendar feed URL. Retrieves the calendar feed URL for the trello board specified by `idboard` for calendar integration.",
)
def TRELLO_ADD_BOARDS_CALENDAR_KEY_GENERATE_BY_ID_BOARD(
    id_board: Annotated[str, "The ID of the board to get calendar feed URL for."]
):
    """Get board calendar feed URL. Retrieves the calendar feed URL for the trello board specified by `idboard` for calendar integration."""
    err = _validate_required({"id_board": id_board}, ["id_board"])
    if err:
        return err
    
    try:
        # Get board information to construct calendar feed URL
        endpoint = f"/boards/{id_board}"
        result = trello_request("GET", endpoint)
        
        # Construct calendar feed URL (this is how Trello calendar feeds work)
        calendar_feed_url = f"https://trello.com/calendar/{id_board}.ics"
        
        return {
            "successful": True,
            "data": {
                "board_info": result,
                "calendar_feed_url": calendar_feed_url,
                "note": "Use this URL in your calendar application to subscribe to board events"
            },
            "action": "get_calendar_feed_url",
            "id_board": id_board,
            "calendar_feed_url": calendar_feed_url,
            "message": f"Successfully retrieved calendar feed URL for board {id_board}"
        }
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to get calendar feed URL: {str(e)}",
            "action": "get_calendar_feed_url",
            "id_board": id_board,
            "message": f"Failed to get calendar feed URL for board {id_board}"
        }


@mcp.tool(
    "TRELLO_ADD_BOARDS_EMAIL_KEY_GENERATE_BY_ID_BOARD",
    description="Generate email key for board. Generates a new email key for the trello board specified by idboard to enable or reset adding cards via email; this invalidates any previously existing email key for the board.",
)
def TRELLO_ADD_BOARDS_EMAIL_KEY_GENERATE_BY_ID_BOARD(
    id_board: Annotated[str, "The ID of the board to generate an email key for."]
):
    """Generate email key for board. Generates a new email key for the trello board specified by idboard to enable or reset adding cards via email; this invalidates any previously existing email key for the board."""
    err = _validate_required({"id_board": id_board}, ["id_board"])
    if err:
        return err
    
    endpoint = f"/boards/{id_board}/emailKey/generate"
    
    result = trello_request("POST", endpoint)
    
    return {
        "successful": True,
        "data": result,
        "action": "generate_email_key",
        "id_board": id_board,
        "message": f"Successfully generated email key for board {id_board}"
    }

@mcp.tool(
    "TRELLO_ADD_BOARDS_LABELS_BY_ID_BOARD",
    description="Add a label to a board. Creates a new label on an existing trello board.",
)
def TRELLO_ADD_BOARDS_LABELS_BY_ID_BOARD(
    id_board: Annotated[str, "The ID of the board to add the label to."],
    name: Annotated[str, "The name of the label to create."],
    color: Annotated[Optional[str], "The color of the label (red, yellow, orange, green, blue, purple, pink, lime, sky, grey)."] = None
):
    """Add a label to a board. Creates a new label on an existing trello board."""
    err = _validate_required({"id_board": id_board, "name": name}, ["id_board", "name"])
    if err:
        return err
    
    endpoint = f"/boards/{id_board}/labels"
    data = {"name": name}
    
    if color is not None:
        data["color"] = color
    
    result = trello_request("POST", endpoint, data=data)
    
    return {
        "successful": True,
        "data": result,
        "action": "add_label_to_board",
        "id_board": id_board,
        "label_name": name,
        "label_color": color,
        "message": f"Successfully added label '{name}' to board {id_board}"
    }

@mcp.tool(
    "TRELLO_ADD_BOARDS_LISTS_BY_ID_BOARD",
    description="Add new list to board. Creates a new, empty list on a specified, existing trello board, typically used as a column or category for organizing cards.",
)
def TRELLO_ADD_BOARDS_LISTS_BY_ID_BOARD(
    id_board: Annotated[str, "The ID of the board to add the list to."],
    name: Annotated[str, "The name of the list to create."],
    pos: Annotated[Optional[str], "Position of the list (top, bottom, or a number)."] = None
):
    """Add new list to board. Creates a new, empty list on a specified, existing trello board, typically used as a column or category for organizing cards."""
    err = _validate_required({"id_board": id_board, "name": name}, ["id_board", "name"])
    if err:
        return err
    
    endpoint = f"/boards/{id_board}/lists"
    data = {"name": name}
    
    if pos is not None:
        data["pos"] = pos
    
    result = trello_request("POST", endpoint, data=data)
    
    return {
        "successful": True,
        "data": result,
        "action": "add_list_to_board",
        "id_board": id_board,
        "list_name": name,
        "list_position": pos,
        "message": f"Successfully added list '{name}' to board {id_board}"
    }

@mcp.tool(
    "TRELLO_ADD_BOARDS_MARK_AS_VIEWED_BY_ID_BOARD",
    description="Mark board as viewed. Marks the trello board specified by idboard as viewed for the current user, exclusively updating its viewed status and potentially influencing its position in user-specific lists and notification settings.",
)
def TRELLO_ADD_BOARDS_MARK_AS_VIEWED_BY_ID_BOARD(
    id_board: Annotated[str, "The ID of the board to mark as viewed."]
):
    """Mark board as viewed. Marks the trello board specified by idboard as viewed for the current user, exclusively updating its viewed status and potentially influencing its position in user-specific lists and notification settings."""
    err = _validate_required({"id_board": id_board}, ["id_board"])
    if err:
        return err
    
    endpoint = f"/boards/{id_board}/markAsViewed"
    
    result = trello_request("POST", endpoint)
    
    return {
        "successful": True,
        "data": result,
        "action": "mark_board_as_viewed",
        "id_board": id_board,
        "message": f"Successfully marked board {id_board} as viewed"
    }

@mcp.tool(
    "TRELLO_ADD_BOARDS_POWER_UPS_BY_ID_BOARD",
    description="Get board power-ups. Retrieves the power-ups available and enabled on the trello board specified by idboard.",
)
def TRELLO_ADD_BOARDS_POWER_UPS_BY_ID_BOARD(
    id_board: Annotated[str, "The ID of the board to get power-ups for."]
):
    """Get board power-ups. Retrieves the power-ups available and enabled on the trello board specified by idboard."""
    err = _validate_required({"id_board": id_board}, ["id_board"])
    if err:
        return err
    
    try:
        # Get board power-ups (this endpoint is still available)
        endpoint = f"/boards/{id_board}/powerUps"
        
        result = trello_request("GET", endpoint)
        
        return {
            "successful": True,
            "data": result,
            "action": "get_board_power_ups",
            "id_board": id_board,
            "message": f"Successfully retrieved power-ups for board {id_board}",
            "note": "Power-up management is now handled through Trello's web interface. This tool shows available power-ups."
        }
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to get board power-ups: {str(e)}. Note: Power-up management may need to be done through Trello's web interface.",
            "action": "get_board_power_ups",
            "id_board": id_board,
            "message": f"Failed to get power-ups for board {id_board}"
        }

@mcp.tool(
    "TRELLO_ADD_CARDS",
    description="Add card. Creates a new card in a trello list; `idlist` is required, and if `idcardsource` is used, the source card must be accessible.",
)
def TRELLO_ADD_CARDS(
    id_list: Annotated[str, "The ID of the list to add the card to (required)."],
    name: Annotated[Optional[str], "The name of the card."] = None,
    desc: Annotated[Optional[str], "Description of the card."] = None,
    closed: Annotated[Optional[str], "Whether the card is closed."] = None,
    due: Annotated[Optional[str], "Due date for the card."] = None,
    file_source: Annotated[Optional[str], "File source for the card."] = None,
    id_attachment_cover: Annotated[Optional[str], "ID of attachment to use as cover."] = None,
    id_board: Annotated[Optional[str], "ID of the board (if different from list's board)."] = None,
    id_card_source: Annotated[Optional[str], "ID of card to copy from."] = None,
    id_labels: Annotated[Optional[str], "Comma-separated list of label IDs."] = None,
    id_members: Annotated[Optional[str], "Comma-separated list of member IDs."] = None,
    keep_from_source: Annotated[Optional[str], "What to keep from the source card."] = None,
    labels: Annotated[Optional[str], "Comma-separated list of label names."] = None,
    pos: Annotated[Optional[str], "Position of the card (top, bottom, or a number)."] = None,
    subscribed: Annotated[Optional[str], "Whether the user is subscribed to the card."] = None,
    url_source: Annotated[Optional[str], "URL source for the card."] = None
):
    """Add card. Creates a new card in a trello list; `idlist` is required, and if `idcardsource` is used, the source card must be accessible."""
    err = _validate_required({"id_list": id_list}, ["id_list"])
    if err:
        return err
    
    endpoint = "/cards"
    data = {"idList": id_list}
    
    # Add optional parameters if provided
    if name is not None:
        data["name"] = name
    if desc is not None:
        data["desc"] = desc
    if closed is not None:
        data["closed"] = closed
    if due is not None:
        data["due"] = due
    if file_source is not None:
        data["fileSource"] = file_source
    if id_attachment_cover is not None:
        data["idAttachmentCover"] = id_attachment_cover
    if id_board is not None:
        data["idBoard"] = id_board
    if id_card_source is not None:
        data["idCardSource"] = id_card_source
    if id_labels is not None:
        data["idLabels"] = id_labels
    if id_members is not None:
        data["idMembers"] = id_members
    if keep_from_source is not None:
        data["keepFromSource"] = keep_from_source
    if labels is not None:
        data["labels"] = labels
    if pos is not None:
        data["pos"] = pos
    if subscribed is not None:
        data["subscribed"] = subscribed
    if url_source is not None:
        data["urlSource"] = url_source
    
    result = trello_request("POST", endpoint, data=data)
    
    return {
        "successful": True,
        "data": result,
        "action": "add_card",
        "id_list": id_list,
        "card_name": name,
        "message": f"Successfully created card in list {id_list}"
    }

@mcp.tool(
    "TRELLO_GET_BOARDS_CARDS_BY_ID_BOARD",
    description="Get cards from board. Retrieves all cards from a specific trello board.",
)
def TRELLO_GET_BOARDS_CARDS_BY_ID_BOARD(
    id_board: Annotated[str, "The ID of the board to get cards from."],
    fields: Annotated[Optional[str], "Fields to return. Defaults to all."] = "all",
    actions: Annotated[Optional[str], "Actions to include."] = None,
    attachments: Annotated[Optional[str], "Whether to include attachments."] = None,
    attachment_fields: Annotated[Optional[str], "Attachment fields to return."] = None,
    members: Annotated[Optional[str], "Whether to include members."] = None,
    member_fields: Annotated[Optional[str], "Member fields to return."] = None,
    check_item_states: Annotated[Optional[str], "Whether to include check item states."] = None,
    checklists: Annotated[Optional[str], "Whether to include checklists."] = None,
    limit: Annotated[Optional[str], "Maximum number of cards to return."] = None,
    since: Annotated[Optional[str], "Only return cards modified since this date."] = None,
    before: Annotated[Optional[str], "Only return cards modified before this date."] = None,
    filter: Annotated[Optional[str], "Filter cards (all, closed, none, open, visible)."] = None
):
    """Get cards from board. Retrieves all cards from a specific trello board."""
    err = _validate_required({"id_board": id_board}, ["id_board"])
    if err:
        return err
    
    endpoint = f"/boards/{id_board}/cards"
    params = {}
    
    if fields != "all":
        params["fields"] = fields
    if actions:
        params["actions"] = actions
    if attachments:
        params["attachments"] = attachments
    if attachment_fields:
        params["attachment_fields"] = attachment_fields
    if members:
        params["members"] = members
    if member_fields:
        params["member_fields"] = member_fields
    if check_item_states:
        params["checkItemStates"] = check_item_states
    if checklists:
        params["checklists"] = checklists
    if limit:
        params["limit"] = limit
    if since:
        params["since"] = since
    if before:
        params["before"] = before
    if filter:
        params["filter"] = filter
    
    result = trello_request("GET", endpoint, params=params)
    
    return {
        "successful": True,
        "data": result,
        "action": "get_cards_from_board",
        "id_board": id_board,
        "card_count": len(result) if isinstance(result, list) else 0,
        "message": f"Successfully retrieved cards from board {id_board}"
    }

@mcp.tool(
    "TRELLO_ADD_CARDS_CHECKLISTS_BY_ID_CARD",
    description="Add checklist to card via id. Adds a checklist to a trello card: use value to add a specific existing checklist, idchecklistsource to create a new checklist by copying an existing one (optionally using name for the new checklist's name), or name to create a new empty checklist from scratch.",
)
def TRELLO_ADD_CARDS_CHECKLISTS_BY_ID_CARD(
    id_card: Annotated[str, "The ID of the card to add the checklist to."],
    value: Annotated[Optional[str], "ID of an existing checklist to add to the card."] = None,
    id_checklist_source: Annotated[Optional[str], "ID of an existing checklist to copy from."] = None,
    name: Annotated[Optional[str], "Name for the new checklist (required when creating new or copying)."] = None
):
    """Add checklist to card via id. Adds a checklist to a trello card: use value to add a specific existing checklist, idchecklistsource to create a new checklist by copying an existing one (optionally using name for the new checklist's name), or name to create a new empty checklist from scratch."""
    err = _validate_required({"id_card": id_card}, ["id_card"])
    if err:
        return err
    
    # Validate that at least one of the three options is provided
    if not value and not id_checklist_source and not name:
        return {
            "successful": False,
            "error": "Must provide either 'value' (existing checklist ID), 'id_checklist_source' (to copy), or 'name' (to create new)",
            "action": "add_checklist_to_card",
            "id_card": id_card,
            "message": "Failed to add checklist: missing required parameter"
        }
    
    # Validate that only one option is provided
    provided_options = sum([bool(value), bool(id_checklist_source), bool(name)])
    if provided_options > 1:
        return {
            "successful": False,
            "error": "Can only provide one of: 'value', 'id_checklist_source', or 'name'",
            "action": "add_checklist_to_card",
            "id_card": id_card,
            "message": "Failed to add checklist: too many parameters provided"
        }
    
    endpoint = f"/cards/{id_card}/checklists"
    data = {}
    
    if value:
        # Add existing checklist to card
        data["value"] = value
        result = trello_request("POST", endpoint, data=data)
        
        return {
            "successful": True,
            "data": result,
            "action": "add_existing_checklist_to_card",
            "id_card": id_card,
            "checklist_id": value,
            "message": f"Successfully added existing checklist {value} to card {id_card}"
        }
    
    elif id_checklist_source:
        # Copy existing checklist
        if not name:
            return {
                "successful": False,
                "error": "Name is required when copying a checklist",
                "action": "add_checklist_to_card",
                "id_card": id_card,
                "message": "Failed to add checklist: name required for copying"
            }
        
        data["idChecklistSource"] = id_checklist_source
        data["name"] = name
        result = trello_request("POST", endpoint, data=data)
        
        return {
            "successful": True,
            "data": result,
            "action": "copy_checklist_to_card",
            "id_card": id_card,
            "source_checklist_id": id_checklist_source,
            "new_checklist_name": name,
            "message": f"Successfully copied checklist {id_checklist_source} as '{name}' to card {id_card}"
        }
    
    elif name:
        # Create new empty checklist
        data["name"] = name
        result = trello_request("POST", endpoint, data=data)
        
        return {
            "successful": True,
            "data": result,
            "action": "create_new_checklist_on_card",
            "id_card": id_card,
            "checklist_name": name,
            "message": f"Successfully created new checklist '{name}' on card {id_card}"
        }

@mcp.tool(
    "TRELLO_ADD_CARDS_ACTIONS_COMMENTS_BY_ID_CARD",
    description="Add comment to card. Adds a new text comment, which can include @mentions, to a trello card specified by its id; file attachments are not supported via this action.",
)
def TRELLO_ADD_CARDS_ACTIONS_COMMENTS_BY_ID_CARD(
    id_card: Annotated[str, "The ID of the card to add the comment to."],
    text: Annotated[str, "The text content of the comment to add."]
):
    """Add comment to card. Adds a new text comment, which can include @mentions, to a trello card specified by its id; file attachments are not supported via this action."""
    err = _validate_required({"id_card": id_card, "text": text}, ["id_card", "text"])
    if err:
        return err
    
    endpoint = f"/cards/{id_card}/actions/comments"
    data = {"text": text}
    
    result = trello_request("POST", endpoint, data=data)
    
    return {
        "successful": True,
        "data": result,
        "action": "add_comment_to_card",
        "id_card": id_card,
        "comment_text": text,
        "message": f"Successfully added comment to card {id_card}"
    }

@mcp.tool(
    "TRELLO_ADD_CARDS_CHECKLIST_CHECK_ITEM_BY_ID_CARD_BY_ID_CHECKLIST",
    description="Add check item to checklist. Adds a new check item to an existing checklist on a specific trello card.",
)
def TRELLO_ADD_CARDS_CHECKLIST_CHECK_ITEM_BY_ID_CARD_BY_ID_CHECKLIST(
    id_card: Annotated[str, "The ID of the card containing the checklist."],
    id_checklist: Annotated[str, "The ID of the checklist to add the check item to."],
    name: Annotated[str, "The name/text of the check item to add."],
    pos: Annotated[Optional[str], "Position of the check item (top, bottom, or a number)."] = None
):
    """Add check item to checklist. Adds a new check item to an existing checklist on a specific trello card."""
    err = _validate_required({"id_card": id_card, "id_checklist": id_checklist, "name": name}, ["id_card", "id_checklist", "name"])
    if err:
        return err
    
    endpoint = f"/cards/{id_card}/checklist/{id_checklist}/checkItem"
    data = {"name": name}
    
    if pos is not None:
        data["pos"] = pos
    
    result = trello_request("POST", endpoint, data=data)
    
    return {
        "successful": True,
        "data": result,
        "action": "add_check_item_to_checklist",
        "id_card": id_card,
        "id_checklist": id_checklist,
        "check_item_name": name,
        "check_item_position": pos,
        "message": f"Successfully added check item '{name}' to checklist {id_checklist} on card {id_card}"
    }

@mcp.tool(
    "TRELLO_ADD_CARDS_ID_LABELS_BY_ID_CARD",
    description="Add label to card. Adds an existing label to a trello card; idcard identifies the card and value is the id of the label to add. both card and label must already exist.",
)
def TRELLO_ADD_CARDS_ID_LABELS_BY_ID_CARD(
    id_card: Annotated[str, "The ID of the card to add the label to."],
    value: Annotated[str, "The ID of the existing label to add to the card."]
):
    """Add label to card. Adds an existing label to a trello card; idcard identifies the card and value is the id of the label to add. both card and label must already exist."""
    err = _validate_required({"id_card": id_card, "value": value}, ["id_card", "value"])
    if err:
        return err
    
    endpoint = f"/cards/{id_card}/idLabels"
    data = {"value": value}
    
    result = trello_request("POST", endpoint, data=data)
    
    return {
        "successful": True,
        "data": result,
        "action": "add_label_to_card",
        "id_card": id_card,
        "label_id": value,
        "message": f"Successfully added label {value} to card {id_card}"
    }

@mcp.tool(
    "TRELLO_ADD_CARDS_ID_MEMBERS_BY_ID_CARD",
    description="Add card member by id. Assigns a trello member to a specific trello card by card id (or short link) and member id.",
)
def TRELLO_ADD_CARDS_ID_MEMBERS_BY_ID_CARD(
    id_card: Annotated[str, "The ID of the card to assign the member to."],
    value: Annotated[str, "The ID of the member to assign to the card."]
):
    """Add card member by id. Assigns a trello member to a specific trello card by card id (or short link) and member id."""
    err = _validate_required({"id_card": id_card, "value": value}, ["id_card", "value"])
    if err:
        return err
    
    endpoint = f"/cards/{id_card}/idMembers"
    data = {"value": value}
    
    result = trello_request("POST", endpoint, data=data)
    
    return {
        "successful": True,
        "data": result,
        "action": "add_member_to_card",
        "id_card": id_card,
        "member_id": value,
        "message": f"Successfully assigned member {value} to card {id_card}"
    }

@mcp.tool(
    "TRELLO_ADD_CARDS_LABELS_BY_ID_CARD",
    description="Add labels to card. Adds a label to an existing trello card (specified by idcard), defining the label by name and either color or the overriding value (which specifies color by name); a new label is created on the board if a matching one (by name/color combination) doesn't already exist.",
)
def TRELLO_ADD_CARDS_LABELS_BY_ID_CARD(
    id_card: Annotated[str, "The ID of the card to add the label to."],
    name: Annotated[str, "The name of the label to add."],
    color: Annotated[Optional[str], "The color of the label (red, yellow, orange, green, blue, purple, pink, lime, sky, grey)."] = None,
    value: Annotated[Optional[str], "Override color by name (red, yellow, orange, green, blue, purple, pink, lime, sky, grey)."] = None
):
    """Add labels to card. Adds a label to an existing trello card (specified by idcard), defining the label by name and either color or the overriding value (which specifies color by name); a new label is created on the board if a matching one (by name/color combination) doesn't already exist."""
    err = _validate_required({"id_card": id_card, "name": name}, ["id_card", "name"])
    if err:
        return err
    
    endpoint = f"/cards/{id_card}/labels"
    data = {"name": name}
    
    # Handle both color and value - value takes precedence over color
    if value:
        data["value"] = value  # value overrides color
        if color:
            # Include color as fallback or additional info
            data["color"] = color
    elif color:
        data["color"] = color  # use color if no value provided
    
    result = trello_request("POST", endpoint, data=data)
    
    return {
        "successful": True,
        "data": result,
        "action": "add_label_to_card",
        "id_card": id_card,
        "label_name": name,
        "label_color": value if value else color,
        "message": f"Successfully added label '{name}' to card {id_card}"
    }

@mcp.tool(
    "TRELLO_ADD_CARDS_STICKERS_BY_ID_CARD",
    description="Add sticker to card. Adds a sticker to a trello card, using a default sticker name (e.g., 'taco-cool') or a custom sticker id for the image, and allows specifying its position, rotation, and z-index.",
)
def TRELLO_ADD_CARDS_STICKERS_BY_ID_CARD(
    id_card: Annotated[str, "The ID of the card to add the sticker to."],
    image: Annotated[str, "The sticker image name (e.g., 'taco-cool') or custom sticker ID."],
    left: Annotated[Optional[str], "Left position of the sticker on the card."] = None,
    top: Annotated[Optional[str], "Top position of the sticker on the card."] = None,
    rotate: Annotated[Optional[str], "Rotation angle of the sticker in degrees."] = None,
    z_index: Annotated[Optional[str], "Z-index (layer order) of the sticker."] = None
):
    """Add sticker to card. Adds a sticker to a trello card, using a default sticker name (e.g., 'taco-cool') or a custom sticker id for the image, and allows specifying its position, rotation, and z-index."""
    err = _validate_required({"id_card": id_card, "image": image}, ["id_card", "image"])
    if err:
        return err
    
    endpoint = f"/cards/{id_card}/stickers"
    data = {"image": image}
    
    # Add optional positioning and styling parameters
    if left is not None:
        data["left"] = left
    if top is not None:
        data["top"] = top
    if rotate is not None:
        data["rotate"] = rotate
    if z_index is not None:
        data["zIndex"] = z_index
    
    result = trello_request("POST", endpoint, data=data)
    
    return {
        "successful": True,
        "data": result,
        "action": "add_sticker_to_card",
        "id_card": id_card,
        "sticker_image": image,
        "position": {
            "left": left,
            "top": top,
            "rotate": rotate,
            "z_index": z_index
        },
        "message": f"Successfully added sticker '{image}' to card {id_card}"
    }

@mcp.tool(
    "TRELLO_ADD_CHECKLISTS",
    description="Add checklist to card. Creates a new checklist on a trello card, either by name or by copying from idchecklistsource, targeting an idcard or idboard; this action creates only the checklist structure, not its items.",
)
def TRELLO_ADD_CHECKLISTS(
    id_card: Annotated[Optional[str], "The ID of the card to add the checklist to."] = None,
    id_board: Annotated[Optional[str], "The ID of the board to add the checklist to."] = None,
    name: Annotated[Optional[str], "The name of the new checklist to create."] = None,
    id_checklist_source: Annotated[Optional[str], "The ID of an existing checklist to copy from."] = None,
    pos: Annotated[Optional[str], "Position of the checklist (top, bottom, or a number)."] = None
):
    """Add checklist to card. Creates a new checklist on a trello card, either by name or by copying from idchecklistsource, targeting an idcard or idboard; this action creates only the checklist structure, not its items."""
    
    # Validate that at least one target is provided
    if not id_card and not id_board:
        return {
            "successful": False,
            "error": "Must provide either 'id_card' or 'id_board' (or both)",
            "action": "add_checklist",
            "message": "Failed to add checklist: missing target (card or board)"
        }
    
    # Validate that either name or id_checklist_source is provided
    if not name and not id_checklist_source:
        return {
            "successful": False,
            "error": "Must provide either 'name' (to create new) or 'id_checklist_source' (to copy)",
            "action": "add_checklist",
            "message": "Failed to add checklist: missing name or source"
        }
    
    data = {}
    
    # Determine endpoint and data based on target
    # Priority: if both provided, use card endpoint (more specific)
    if id_card:
        endpoint = f"/cards/{id_card}/checklists"
        target_type = "card"
        target_id = id_card
        if id_board:
            # Include board info in the data for reference
            data["idBoard"] = id_board
    else:
        endpoint = f"/boards/{id_board}/checklists"
        target_type = "board"
        target_id = id_board
    
    # Handle both name and source - if both provided, copy and rename
    if id_checklist_source:
        data["idChecklistSource"] = id_checklist_source
        if name:
            data["name"] = name  # Override the name when copying
        action_type = "copy_checklist"
        message = f"Successfully copied checklist {id_checklist_source} to {target_type} {target_id}"
        if name:
            message += f" as '{name}'"
    elif name:
        data["name"] = name  # Create new list with this name
        action_type = "create_new_checklist"
        message = f"Successfully created new checklist '{name}' on {target_type} {target_id}"
    
    if pos is not None:
        data["pos"] = pos
    
    result = trello_request("POST", endpoint, data=data)
    
    return {
        "successful": True,
        "data": result,
        "action": action_type,
        "target_type": target_type,
        "target_id": target_id,
        "checklist_name": name,
        "source_checklist_id": id_checklist_source,
        "position": pos,
        "message": message
    }

@mcp.tool(
    "TRELLO_ADD_CHECKLISTS_CHECK_ITEMS_BY_ID_CHECKLIST",
    description="Add check item to checklist. Adds a new check item to a specified trello checklist; this action does not update existing check items.",
)
def TRELLO_ADD_CHECKLISTS_CHECK_ITEMS_BY_ID_CHECKLIST(
    id_checklist: Annotated[str, "The ID of the checklist to add the check item to."],
    name: Annotated[str, "The name/text of the check item to add."],
    checked: Annotated[Optional[str], "Whether the check item should be checked (true/false)."] = None,
    pos: Annotated[Optional[str], "Position of the check item (top, bottom, or a number)."] = None
):
    """Add check item to checklist. Adds a new check item to a specified trello checklist; this action does not update existing check items."""
    err = _validate_required({"id_checklist": id_checklist, "name": name}, ["id_checklist", "name"])
    if err:
        return err
    
    endpoint = f"/checklists/{id_checklist}/checkItems"
    data = {"name": name}
    
    # Add optional parameters
    if checked is not None:
        data["checked"] = checked
    if pos is not None:
        data["pos"] = pos
    
    result = trello_request("POST", endpoint, data=data)
    
    return {
        "successful": True,
        "data": result,
        "action": "add_check_item_to_checklist",
        "id_checklist": id_checklist,
        "check_item_name": name,
        "checked": checked,
        "position": pos,
        "message": f"Successfully added check item '{name}' to checklist {id_checklist}"
    }

@mcp.tool(
    "TRELLO_ADD_LABELS",
    description="Create label on board. Creates a new label with a specified name (required) and color on a trello board (idboard required); this action defines the label but does not apply it to cards.",
)
def TRELLO_ADD_LABELS(
    id_board: Annotated[str, "The ID of the board to create the label on."],
    name: Annotated[str, "The name of the label to create."],
    color: Annotated[Optional[str], "The color of the label (red, yellow, orange, green, blue, purple, pink, lime, sky, grey)."] = None
):
    """Create label on board. Creates a new label with a specified name (required) and color on a trello board (idboard required); this action defines the label but does not apply it to cards."""
    err = _validate_required({"id_board": id_board, "name": name}, ["id_board", "name"])
    if err:
        return err
    
    endpoint = f"/boards/{id_board}/labels"
    data = {"name": name}
    
    if color is not None:
        data["color"] = color
    
    result = trello_request("POST", endpoint, data=data)
    
    return {
        "successful": True,
        "data": result,
        "action": "create_label_on_board",
        "id_board": id_board,
        "label_name": name,
        "label_color": color,
        "label_id": result.get("id") if isinstance(result, dict) else None,
        "message": f"Successfully created label '{name}' on board {id_board}"
    }

@mcp.tool(
    "TRELLO_ADD_LISTS",
    description="Add new list to board. Creates a new list on a specified trello board, with options to copy an existing list, set its position, initial state (archived/subscribed), and does not modify existing lists or move cards.",
)
def TRELLO_ADD_LISTS(
    id_board: Annotated[str, "The ID of the board to create the list on."],
    name: Annotated[str, "The name of the list to create."],
    id_list_source: Annotated[Optional[str], "The ID of an existing list to copy from."] = None,
    pos: Annotated[Optional[str], "Position of the list (top, bottom, or a number)."] = None,
    closed: Annotated[Optional[str], "Whether the list should be closed/archived (true/false)."] = None,
    subscribed: Annotated[Optional[str], "Whether the user should be subscribed to the list (true/false)."] = None
):
    """Add new list to board. Creates a new list on a specified trello board, with options to copy an existing list, set its position, initial state (archived/subscribed), and does not modify existing lists or move cards."""
    err = _validate_required({"id_board": id_board}, ["id_board"])
    if err:
        return err
    
    # Validate that either name or id_list_source is provided
    if not name and not id_list_source:
        return {
            "successful": False,
            "error": "Must provide either 'name' (to create new) or 'id_list_source' (to copy)",
            "action": "add_list_to_board",
            "id_board": id_board,
            "message": "Failed to add list: missing name or source"
        }
    
    endpoint = f"/boards/{id_board}/lists"
    data = {}
    
    # Handle both name and source - if both provided, copy and rename
    if id_list_source:
        data["idListSource"] = id_list_source
        if name:
            data["name"] = name  # Override the name when copying
    elif name:
        data["name"] = name  # Create new list with this name
    
    # Add optional parameters
    if pos is not None:
        data["pos"] = pos
    if closed is not None:
        data["closed"] = closed
    if subscribed is not None:
        data["subscribed"] = subscribed
    
    result = trello_request("POST", endpoint, data=data)
    
    return {
        "successful": True,
        "data": result,
        "action": "add_list_to_board",
        "id_board": id_board,
        "list_name": name,
        "source_list_id": id_list_source,
        "position": pos,
        "closed": closed,
        "subscribed": subscribed,
        "list_id": result.get("id") if isinstance(result, dict) else None,
        "message": f"Successfully created list '{name}' on board {id_board}"
    }





@mcp.tool(
    "TRELLO_ADD_LISTS_ARCHIVE_ALL_CARDS_BY_ID_LIST",
    description="Archive all cards in list. Archives all cards in a trello list; while cards can be restored via the trello interface, this action does not provide an unarchive function.",
)
def TRELLO_ADD_LISTS_ARCHIVE_ALL_CARDS_BY_ID_LIST(
    id_list: Annotated[str, "The ID of the list to archive all cards from."]
):
    """Archive all cards in list. Archives all cards in a trello list; while cards can be restored via the trello interface, this action does not provide an unarchive function."""
    err = _validate_required({"id_list": id_list}, ["id_list"])
    if err:
        return err
    
    endpoint = f"/lists/{id_list}/archiveAllCards"
    
    result = trello_request("POST", endpoint)
    
    return {
        "successful": True,
        "data": result,
        "action": "archive_all_cards_in_list",
        "id_list": id_list,
        "message": f"Successfully archived all cards in list {id_list}"
    }

@mcp.tool(
    "TRELLO_ADD_LISTS_CARDS_BY_ID_LIST",
    description="Add card to list. Creates a new card in a trello list, which must be specified by an existing and accessible idlist.",
)
def TRELLO_ADD_LISTS_CARDS_BY_ID_LIST(
    id_list: Annotated[str, "The ID of the list to add the card to."],
    name: Annotated[Optional[str], "The name of the card to create."] = None,
    desc: Annotated[Optional[str], "Description of the card."] = None,
    due: Annotated[Optional[str], "Due date for the card."] = None,
    id_members: Annotated[Optional[str], "Comma-separated list of member IDs to assign to the card."] = None,
    labels: Annotated[Optional[str], "Comma-separated list of label names or IDs to add to the card."] = None
):
    """Add card to list. Creates a new card in a trello list, which must be specified by an existing and accessible idlist."""
    err = _validate_required({"id_list": id_list}, ["id_list"])
    if err:
        return err
    
    endpoint = "/cards"
    data = {"idList": id_list}
    
    # Add optional parameters
    if name is not None:
        data["name"] = name
    if desc is not None:
        data["desc"] = desc
    if due is not None:
        data["due"] = due
    if id_members is not None:
        data["idMembers"] = id_members
    if labels is not None:
        data["labels"] = labels
    
    result = trello_request("POST", endpoint, data=data)
    
    return {
        "successful": True,
        "data": result,
        "action": "add_card_to_list",
        "id_list": id_list,
        "card_name": name,
        "card_description": desc,
        "due_date": due,
        "member_ids": id_members,
        "labels": labels,
        "card_id": result.get("id") if isinstance(result, dict) else None,
        "message": f"Successfully created card in list {id_list}"
    }

@mcp.tool(
    "TRELLO_ADD_LISTS_MOVE_ALL_CARDS_BY_ID_LIST",
    description="Move all cards in list to board. Moves all cards from a trello list to a different board; this action is irreversible, moves (not copies) cards, and empties the source list without deleting it.",
)
def TRELLO_ADD_LISTS_MOVE_ALL_CARDS_BY_ID_LIST(
    id_list: Annotated[str, "The ID of the list to move all cards from."],
    id_board: Annotated[str, "The ID of the destination board to move cards to."]
):
    """Move all cards in list to board. Moves all cards from a trello list to a different board; this action is irreversible, moves (not copies) cards, and empties the source list without deleting it."""
    err = _validate_required({"id_list": id_list, "id_board": id_board}, ["id_list", "id_board"])
    if err:
        return err
    
    try:
        # First, get all cards from the source list
        cards_endpoint = f"/lists/{id_list}/cards"
        cards_result = trello_request("GET", cards_endpoint)
        
        if not isinstance(cards_result, list):
            return {
                "successful": False,
                "error": "Failed to retrieve cards from source list",
                "action": "move_all_cards_from_list_to_board",
                "id_list": id_list,
                "destination_board_id": id_board,
                "message": "Failed to move cards: could not retrieve cards from source list"
            }
        
        if not cards_result:
            return {
                "successful": True,
                "data": {"moved_cards": 0, "cards": []},
                "action": "move_all_cards_from_list_to_board",
                "id_list": id_list,
                "destination_board_id": id_board,
                "moved_cards_count": 0,
                "message": "No cards found in source list to move"
            }
        
        # Get the first list from the destination board to move cards to
        board_lists_endpoint = f"/boards/{id_board}/lists"
        board_lists_result = trello_request("GET", board_lists_endpoint)
        
        if not isinstance(board_lists_result, list) or not board_lists_result:
            return {
                "successful": False,
                "error": "Failed to retrieve lists from destination board",
                "action": "move_all_cards_from_list_to_board",
                "id_list": id_list,
                "destination_board_id": id_board,
                "message": "Failed to move cards: could not find lists in destination board"
            }
        
        # Use the first list in the destination board
        destination_list_id = board_lists_result[0].get("id")
        if not destination_list_id:
            return {
                "successful": False,
                "error": "No valid list found in destination board",
                "action": "move_all_cards_from_list_to_board",
                "id_list": id_list,
                "destination_board_id": id_board,
                "message": "Failed to move cards: no valid list in destination board"
            }
        
        # Move each card to the destination list
        moved_cards = []
        failed_cards = []
        
        for card in cards_result:
            card_id = card.get("id")
            if not card_id:
                continue
                
            try:
                # Move the card to the destination list
                move_endpoint = f"/cards/{card_id}"
                move_data = {"idList": destination_list_id}
                move_result = trello_request("PUT", move_endpoint, data=move_data)
                moved_cards.append({
                    "id": card_id,
                    "name": card.get("name", "Unknown"),
                    "destination_list_id": destination_list_id
                })
            except Exception as e:
                failed_cards.append({
                    "id": card_id,
                    "name": card.get("name", "Unknown"),
                    "error": str(e)
                })
        
        return {
            "successful": True,
            "data": {
                "moved_cards": moved_cards,
                "failed_cards": failed_cards,
                "total_cards": len(cards_result),
                "successfully_moved": len(moved_cards),
                "failed": len(failed_cards)
            },
            "action": "move_all_cards_from_list_to_board",
            "id_list": id_list,
            "destination_board_id": id_board,
            "destination_list_id": destination_list_id,
            "moved_cards_count": len(moved_cards),
            "failed_cards_count": len(failed_cards),
            "message": f"Successfully moved {len(moved_cards)} out of {len(cards_result)} cards from list {id_list} to board {id_board}"
        }
        
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to move cards: {str(e)}",
            "action": "move_all_cards_from_list_to_board",
            "id_list": id_list,
            "destination_board_id": id_board,
            "message": f"Failed to move cards from list {id_list} to board {id_board}"
        }

@mcp.tool(
    "TRELLO_ADD_MEMBERS_BOARD_STARS_BY_ID_MEMBER",
    description="Add board star to member. Stars a trello board for a member (does not remove or list stars), optionally at a specified position; the board must exist and be accessible to the member.",
)
def TRELLO_ADD_MEMBERS_BOARD_STARS_BY_ID_MEMBER(
    id_member: Annotated[str, "The ID of the member to star the board for."],
    id_board: Annotated[str, "The ID of the board to star."],
    pos: Annotated[str, "Optional position for the starred board."] = None
):
    """Add board star to member. Stars a trello board for a member (does not remove or list stars), optionally at a specified position; the board must exist and be accessible to the member."""
    err = _validate_required({"id_member": id_member, "id_board": id_board}, ["id_member", "id_board"])
    if err:
        return err
    
    endpoint = f"/members/{id_member}/boardStars"
    data = {"idBoard": id_board}
    
    if pos:
        data["pos"] = pos
    
    result = trello_request("POST", endpoint, data=data)
    
    return {
        "successful": True,
        "data": result,
        "action": "add_board_star",
        "member_id": id_member,
        "board_id": id_board,
        "position": pos,
        "message": f"Successfully starred board {id_board} for member {id_member}"
        }

@mcp.tool(
    "TRELLO_ADD_MEMBERS_SAVED_SEARCHES_BY_ID_MEMBER",
    description="Add saved search for member. Creates a new saved search with a specified name, position, and query for a trello member.",
)
def TRELLO_ADD_MEMBERS_SAVED_SEARCHES_BY_ID_MEMBER(
    id_member: Annotated[str, "The ID of the member to create the saved search for."],
    name: Annotated[str, "The name of the saved search."],
    pos: Annotated[str, "The position of the saved search."],
    query: Annotated[str, "The search query for the saved search."]
):
    """Add saved search for member. Creates a new saved search with a specified name, position, and query for a trello member."""
    err = _validate_required({"id_member": id_member, "name": name, "pos": pos, "query": query}, ["id_member", "name", "pos", "query"])
    if err:
        return err
    
    endpoint = f"/members/{id_member}/savedSearches"
    data = {
        "name": name,
        "pos": pos,
        "query": query
    }
    
    result = trello_request("POST", endpoint, data=data)
    
    return {
        "successful": True,
        "data": result,
        "action": "add_saved_search",
        "member_id": id_member,
        "search_name": name,
        "position": pos,
        "query": query,
        "message": f"Successfully created saved search '{name}' for member {id_member}"
        }

@mcp.tool(
    "TRELLO_ADD_NOTIFICATIONS_ALL_READ",
    description="Mark all notifications as read. Marks all trello notifications for the authenticated user as read across all boards; this action is permanent and cannot be undone.",
)
def TRELLO_ADD_NOTIFICATIONS_ALL_READ():
    """Mark all notifications as read. Marks all trello notifications for the authenticated user as read across all boards; this action is permanent and cannot be undone."""
    endpoint = "/notifications/all/read"
    
    result = trello_request("POST", endpoint)
    
    return {
        "successful": True,
        "data": result,
        "action": "mark_all_notifications_read",
        "message": "Successfully marked all notifications as read"
        }

@mcp.tool(
    "TRELLO_ADD_ORGANIZATIONS",
    description="Create organization. Creates a new trello organization (workspace) with a displayname (required), and optionally a description, website, and various preferences (e.g., board visibility, member invitation restrictions).",
)
def TRELLO_ADD_ORGANIZATIONS(
    display_name: Annotated[str, "The display name of the organization (required)."],
    desc: Annotated[str, "Description of the organization."] = None,
    name: Annotated[str, "The name of the organization."] = None,
    website: Annotated[str, "Website URL of the organization."] = None,
    prefs__associated_domain: Annotated[str, "Associated domain for the organization."] = None,
    prefs__board_visibility_restrict__org: Annotated[str, "Restrict board visibility to organization members."] = None,
    prefs__board_visibility_restrict__private: Annotated[str, "Restrict private board visibility."] = None,
    prefs__board_visibility_restrict__public: Annotated[str, "Restrict public board visibility."] = None,
    prefs__external_members_disabled: Annotated[str, "Disable external members."] = None,
    prefs__google_apps_version: Annotated[str, "Google Apps version."] = None,
    prefs__org_invite_restrict: Annotated[str, "Organization invite restrictions."] = None,
    prefs__permission_level: Annotated[str, "Permission level for the organization."] = None
):
    """Create organization. Creates a new trello organization (workspace) with a displayname (required), and optionally a description, website, and various preferences (e.g., board visibility, member invitation restrictions)."""
    err = _validate_required({"display_name": display_name}, ["display_name"])
    if err:
        return err
    
    endpoint = "/organizations"
    data = {"displayName": display_name}
    
    # Add optional parameters if provided
    if desc:
        data["desc"] = desc
    if name:
        data["name"] = name
    if website:
        data["website"] = website
    
    # Add preferences if provided
    if prefs__associated_domain:
        data["prefs/associatedDomain"] = prefs__associated_domain
    if prefs__board_visibility_restrict__org:
        data["prefs/boardVisibilityRestrict/org"] = prefs__board_visibility_restrict__org
    if prefs__board_visibility_restrict__private:
        data["prefs/boardVisibilityRestrict/private"] = prefs__board_visibility_restrict__private
    if prefs__board_visibility_restrict__public:
        data["prefs/boardVisibilityRestrict/public"] = prefs__board_visibility_restrict__public
    if prefs__external_members_disabled:
        data["prefs/externalMembersDisabled"] = prefs__external_members_disabled
    if prefs__google_apps_version:
        data["prefs/googleAppsVersion"] = prefs__google_apps_version
    if prefs__org_invite_restrict:
        data["prefs/orgInviteRestrict"] = prefs__org_invite_restrict
    if prefs__permission_level:
        data["prefs/permissionLevel"] = prefs__permission_level
    
    result = trello_request("POST", endpoint, data=data)
    
    return {
        "successful": True,
        "data": result,
        "action": "create_organization",
        "organization_name": display_name,
        "organization_id": result.get("id") if isinstance(result, dict) else None,
        "message": f"Successfully created organization '{display_name}'"
        }

@mcp.tool(
    "TRELLO_ADD_TOKENS_WEBHOOKS_BY_TOKEN",
    description="Add token webhook. Creates a webhook for a trello token to monitor a trello model (idmodel) and send notifications to a callbackurl, which must be publicly accessible and able to respond to trello's head validation request.",
)
def TRELLO_ADD_TOKENS_WEBHOOKS_BY_TOKEN(
    callback_url: Annotated[str, "The callback URL where Trello will send webhook notifications. Must be publicly accessible."],
    id_model: Annotated[str, "The ID of the Trello model (board, card, etc.) to monitor."],
    description: Annotated[str, "Description of the webhook."] = ""
):
    """Add token webhook. Creates a webhook for a trello token to monitor a trello model (idmodel) and send notifications to a callbackurl, which must be publicly accessible and able to respond to trello's head validation request."""
    err = _validate_required({"callback_url": callback_url, "id_model": id_model}, ["callback_url", "id_model"])
    if err:
        return err
    
    endpoint = "/tokens/{token}/webhooks"
    data = {
        "callbackURL": callback_url,
        "idModel": id_model
    }
    
    if description and description.strip():
        data["description"] = description
    
    result = trello_request("POST", endpoint, data=data)
    
    return {
        "successful": True,
        "data": result,
        "action": "create_webhook",
        "callback_url": callback_url,
        "model_id": id_model,
        "description": description,
        "webhook_id": result.get("id") if isinstance(result, dict) else None,
        "message": f"Successfully created webhook for model {id_model} with callback URL {callback_url}"
        }

@mcp.tool(
    "TRELLO_BOARD_CREATE_BOARD",
    description="Add board. <<deprecated: this action is deprecated. please use 'add boards' instead.>> creates a new trello board, requiring the 'name' parameter.",
)
def TRELLO_BOARD_CREATE_BOARD(
    name: Annotated[str, "The name of the board (required)."],
    desc: Annotated[str, "Description of the board."] = None,
    closed: Annotated[str, "Whether the board is closed."] = None,
    id_board_source: Annotated[str, "ID of a board to copy from."] = None,
    id_organization: Annotated[str, "ID of the organization to add the board to."] = None,
    keep_from_source: Annotated[str, "What to keep from the source board."] = None,
    subscribed: Annotated[str, "Whether the user is subscribed to the board."] = None,
    power_ups: Annotated[str, "Power-ups to enable on the board."] = None,
    # Label names
    label_names__blue: Annotated[str, "Name for blue label."] = None,
    label_names__green: Annotated[str, "Name for green label."] = None,
    label_names__orange: Annotated[str, "Name for orange label."] = None,
    label_names__purple: Annotated[str, "Name for purple label."] = None,
    label_names__red: Annotated[str, "Name for red label."] = None,
    label_names__yellow: Annotated[str, "Name for yellow label."] = None,
    # Preferences (new format)
    prefs__background: Annotated[str, "Background preference for the board."] = None,
    prefs__calendar_feed_enabled: Annotated[str, "Whether calendar feed is enabled."] = None,
    prefs__card_aging: Annotated[str, "Card aging preference."] = None,
    prefs__card_covers: Annotated[str, "Card covers preference."] = None,
    prefs__comments: Annotated[str, "Comments preference."] = None,
    prefs__invitations: Annotated[str, "Invitations preference."] = None,
    prefs__permission_level: Annotated[str, "Permission level for the board."] = None,
    prefs__self_join: Annotated[str, "Self-join preference."] = None,
    prefs__voting: Annotated[str, "Voting preference."] = None,
    # Preferences (old format)
    prefs_background: Annotated[str, "Background preference (old format)."] = None,
    prefs_card_aging: Annotated[str, "Card aging preference (old format)."] = None,
    prefs_card_covers: Annotated[str, "Card covers preference (old format)."] = None,
    prefs_comments: Annotated[str, "Comments preference (old format)."] = None,
    prefs_invitations: Annotated[str, "Invitations preference (old format)."] = None,
    prefs_permission_level: Annotated[str, "Permission level (old format)."] = None,
    prefs_self_join: Annotated[str, "Self-join preference (old format)."] = None,
    prefs_voting: Annotated[str, "Voting preference (old format)."] = None
):
    """Add board. <<deprecated: this action is deprecated. please use 'add boards' instead.>> creates a new trello board, requiring the 'name' parameter."""
    err = _validate_required({"name": name}, ["name"])
    if err:
        return err
    
    endpoint = "/boards"
    data = {"name": name}
    
    # Add basic parameters
    if desc:
        data["desc"] = desc
    if closed:
        data["closed"] = closed
    if id_board_source:
        data["idBoardSource"] = id_board_source
    if id_organization:
        data["idOrganization"] = id_organization
    if keep_from_source:
        data["keepFromSource"] = keep_from_source
    if subscribed:
        data["subscribed"] = subscribed
    if power_ups:
        data["powerUps"] = power_ups
    
    # Add label names
    label_names = {}
    if label_names__blue:
        label_names["blue"] = label_names__blue
    if label_names__green:
        label_names["green"] = label_names__green
    if label_names__orange:
        label_names["orange"] = label_names__orange
    if label_names__purple:
        label_names["purple"] = label_names__purple
    if label_names__red:
        label_names["red"] = label_names__red
    if label_names__yellow:
        label_names["yellow"] = label_names__yellow
    
    if label_names:
        data["labelNames"] = label_names
    
    # Add preferences (new format takes precedence)
    prefs = {}
    if prefs__background:
        prefs["background"] = prefs__background
    elif prefs_background:
        prefs["background"] = prefs_background
        
    if prefs__calendar_feed_enabled:
        prefs["calendarFeedEnabled"] = prefs__calendar_feed_enabled
        
    if prefs__card_aging:
        prefs["cardAging"] = prefs__card_aging
    elif prefs_card_aging:
        prefs["cardAging"] = prefs_card_aging
        
    if prefs__card_covers:
        prefs["cardCovers"] = prefs__card_covers
    elif prefs_card_covers:
        prefs["cardCovers"] = prefs_card_covers
        
    if prefs__comments:
        prefs["comments"] = prefs__comments
    elif prefs_comments:
        prefs["comments"] = prefs_comments
        
    if prefs__invitations:
        prefs["invitations"] = prefs__invitations
    elif prefs_invitations:
        prefs["invitations"] = prefs_invitations
        
    if prefs__permission_level:
        prefs["permissionLevel"] = prefs__permission_level
    elif prefs_permission_level:
        prefs["permissionLevel"] = prefs_permission_level
        
    if prefs__self_join:
        prefs["selfJoin"] = prefs__self_join
    elif prefs_self_join:
        prefs["selfJoin"] = prefs_self_join
        
    if prefs__voting:
        prefs["voting"] = prefs__voting
    elif prefs_voting:
        prefs["voting"] = prefs_voting
    
    if prefs:
        data["prefs"] = prefs
    
    result = trello_request("POST", endpoint, data=data)
    
    return {
        "successful": True,
        "data": result,
        "action": "create_board",
        "board_name": name,
        "board_id": result.get("id") if isinstance(result, dict) else None,
        "organization_id": id_organization,
        "message": f"Successfully created board '{name}'"
        }

@mcp.tool(
    "TRELLO_BOARD_FILTER_CARDS_BY_ID_BOARD",
    description="Get cards by filter from board. Deprecated: use `get boards cards by id board by filter`. retrieves cards from a trello board using a filter.",
)
def TRELLO_BOARD_FILTER_CARDS_BY_ID_BOARD(
    id_board: Annotated[str, "The ID of the board to get cards from."],
    filter: Annotated[str, "The filter to apply when retrieving cards."]
):
    """Get cards by filter from board. Deprecated: use `get boards cards by id board by filter`. retrieves cards from a trello board using a filter."""
    err = _validate_required({"id_board": id_board, "filter": filter}, ["id_board", "filter"])
    if err:
        return err
    
    endpoint = f"/boards/{id_board}/cards"
    params = {"filter": filter}
    
    result = trello_request("GET", endpoint, params=params)
    
    return {
        "successful": True,
        "data": result,
        "action": "get_cards_by_filter",
        "board_id": id_board,
        "filter": filter,
        "cards_count": len(result) if isinstance(result, list) else 0,
        "message": f"Successfully retrieved cards from board {id_board} with filter '{filter}'"
    }

@mcp.tool(
    "TRELLO_BOARD_GET_LISTS_BY_ID_BOARD",
    description="Get board's lists. Deprecated: retrieves lists from a specified trello board; use `get boards lists by id board`.",
)
def TRELLO_BOARD_GET_LISTS_BY_ID_BOARD(
    id_board: Annotated[str, "The ID of the board to get lists from."],
    fields: Annotated[str, "Fields to return. Defaults to all."] = "",
    filter: Annotated[str, "Filter for lists. Defaults to open."] = "",
    cards: Annotated[str, "Cards to include. Defaults to none."] = "",
    card_fields: Annotated[str, "Card fields to return. Defaults to all."] = ""
):
    """Get board's lists. Deprecated: retrieves lists from a specified trello board; use `get boards lists by id board`."""
    err = _validate_required({"id_board": id_board}, ["id_board"])
    if err:
        return err
    
    endpoint = f"/boards/{id_board}/lists"
    params = {}
    
    # Add optional parameters if provided (non-empty strings)
    if fields and fields.strip():
        params["fields"] = fields
    if filter and filter.strip():
        params["filter"] = filter
    if cards and cards.strip():
        params["cards"] = cards
    if card_fields and card_fields.strip():
        params["card_fields"] = card_fields
    
    result = trello_request("GET", endpoint, params=params)
    
    return {
        "successful": True,
        "data": result,
        "action": "get_board_lists",
        "board_id": id_board,
        "lists_count": len(result) if isinstance(result, list) else 0,
        "message": f"Successfully retrieved lists from board {id_board}"
    }

@mcp.tool(
    "TRELLO_CARD_GET_BY_ID_FIELD",
    description="Get card field by id. (deprecated: use `get cards by id card by field` instead) retrieves the value of a single, specified field from a trello card. Use 'all' to get all fields.",
)
def TRELLO_CARD_GET_BY_ID_FIELD(
    id_card: Annotated[str, "The ID of the card to get the field from."],
    field: Annotated[str, "The field name to retrieve from the card. Use 'all' to get all fields."]
):
    """Get card field by id. (deprecated: use `get cards by id card by field` instead) retrieves the value of a single, specified field from a trello card. Use 'all' to get all fields."""
    err = _validate_required({"id_card": id_card, "field": field}, ["id_card", "field"])
    if err:
        return err
    
    # Handle special case for "all" field
    if field.lower() == "all":
        endpoint = f"/cards/{id_card}"
        result = trello_request("GET", endpoint)
        
        return {
            "successful": True,
            "data": result,
            "action": "get_all_card_fields",
            "card_id": id_card,
            "field": "all",
            "available_fields": list(result.keys()) if isinstance(result, dict) else [],
            "message": f"Successfully retrieved all fields from card {id_card}"
        }
    else:
        # Handle specific field
        endpoint = f"/cards/{id_card}/{field}"
        result = trello_request("GET", endpoint)
        
        return {
            "successful": True,
            "data": result,
            "action": "get_card_field",
            "card_id": id_card,
            "field": field,
            "field_value": result,
            "message": f"Successfully retrieved field '{field}' from card {id_card}"
        }

@mcp.tool(
    "TRELLO_CARD_UPDATE_ID_LIST_BY_ID_CARD",
    description="Update card list ID. Deprecated: moves a trello card to a different list on the same board. use `update cards id list by id card` instead.",
)
def TRELLO_CARD_UPDATE_ID_LIST_BY_ID_CARD(
    id_card: Annotated[str, "The ID of the card to move."],
    value: Annotated[str, "The ID of the destination list to move the card to."]
):
    """Update card list ID. Deprecated: moves a trello card to a different list on the same board. use `update cards id list by id card` instead."""
    err = _validate_required({"id_card": id_card, "value": value}, ["id_card", "value"])
    if err:
        return err
    
    endpoint = f"/cards/{id_card}"
    data = {"idList": value}
    
    result = trello_request("PUT", endpoint, data=data)
    
    return {
        "successful": True,
        "data": result,
        "action": "update_card_list",
        "card_id": id_card,
        "destination_list_id": value,
        "card_name": result.get("name") if isinstance(result, dict) else None,
        "message": f"Successfully moved card {id_card} to list {value}"
    }

@mcp.tool(
    "TRELLO_CARD_UPDATE_POS_BY_ID_CARD",
    description="Update card position. Updates a trello card's position within its list to 'top', 'bottom', or a specified 1-indexed positive integer.<<DEPRECATED use update_cards_pos_by_id_card>>",
)
def TRELLO_CARD_UPDATE_POS_BY_ID_CARD(
    id_card: Annotated[str, "The ID of the card to update position for."],
    value: Annotated[str, "The position value: 'top', 'bottom', or a 1-indexed positive integer."]
):
    """Update card position. Updates a trello card's position within its list to 'top', 'bottom', or a specified 1-indexed positive integer.<<DEPRECATED use update_cards_pos_by_id_card>>"""
    err = _validate_required({"id_card": id_card, "value": value}, ["id_card", "value"])
    if err:
        return err
    
    endpoint = f"/cards/{id_card}"
    
    # Handle position value
    if value.lower() == "top":
        pos_data = "top"
    elif value.lower() == "bottom":
        pos_data = "bottom"
    else:
        # Try to parse as integer
        try:
            pos_int = int(value)
            if pos_int <= 0:
                return {
                    "successful": False,
                    "error": "Position must be 'top', 'bottom', or a positive integer",
                    "action": "update_card_position",
                    "card_id": id_card,
                    "value": value,
                    "message": "Invalid position value: must be 'top', 'bottom', or a positive integer"
                }
            pos_data = pos_int
        except ValueError:
            return {
                "successful": False,
                "error": "Position must be 'top', 'bottom', or a positive integer",
                "action": "update_card_position",
                "card_id": id_card,
                "value": value,
                "message": "Invalid position value: must be 'top', 'bottom', or a positive integer"
            }
    
    data = {"pos": pos_data}
    
    result = trello_request("PUT", endpoint, data=data)
    
    return {
        "successful": True,
        "data": result,
        "action": "update_card_position",
        "card_id": id_card,
        "position": value,
        "card_name": result.get("name") if isinstance(result, dict) else None,
        "message": f"Successfully updated card {id_card} position to {value}"
    }

@mcp.tool(
    "TRELLO_CONVERT_CHECKLIST_ITEM_TO_CARD",
    description="Convert checklist item to card. Converts a checklist item into a new card (useful for promoting a subtask), which inherits some properties from the item; this is irreversible via the api and offers no customization during conversion.",
)
def TRELLO_CONVERT_CHECKLIST_ITEM_TO_CARD(
    id_card: Annotated[str, "The ID of the card containing the checklist."],
    id_checklist: Annotated[str, "The ID of the checklist containing the item."],
    id_check_item: Annotated[str, "The ID of the checklist item to convert to a card."]
):
    """Convert checklist item to card. Converts a checklist item into a new card (useful for promoting a subtask), which inherits some properties from the item; this is irreversible via the api and offers no customization during conversion."""
    err = _validate_required({"id_card": id_card, "id_checklist": id_checklist, "id_check_item": id_check_item}, ["id_card", "id_checklist", "id_check_item"])
    if err:
        return err
    
    endpoint = f"/cards/{id_card}/checklist/{id_checklist}/checkItem/{id_check_item}/convertToCard"
    
    result = trello_request("POST", endpoint)
    
    return {
        "successful": True,
        "data": result,
        "action": "convert_checklist_item_to_card",
        "card_id": id_card,
        "checklist_id": id_checklist,
        "check_item_id": id_check_item,
        "new_card_id": result.get("id") if isinstance(result, dict) else None,
        "new_card_name": result.get("name") if isinstance(result, dict) else None,
        "message": f"Successfully converted checklist item {id_check_item} to a new card"
    }

@mcp.tool(
    "TRELLO_GET_ACTIONS_BOARD_BY_ID_ACTION",
    description="Get board by action id. Retrieves details for the trello board associated with a specific action id, returning board information only.",
)
def TRELLO_GET_ACTIONS_BOARD_BY_ID_ACTION(
    id_action: Annotated[str, "The ID of the action to get the board for."],
    fields: Annotated[str, "Fields to return. Defaults to all."] = ""
):
    """Get board by action id. Retrieves details for the trello board associated with a specific action id, returning board information only."""
    err = _validate_required({"id_action": id_action}, ["id_action"])
    if err:
        return err
    
    endpoint = f"/actions/{id_action}/board"
    params = {}
    
    # Add optional fields parameter if provided
    if fields and fields.strip():
        params["fields"] = fields
    
    result = trello_request("GET", endpoint, params=params)
    
    return {
        "successful": True,
        "data": result,
        "action": "get_board_by_action_id",
        "action_id": id_action,
        "board_id": result.get("id") if isinstance(result, dict) else None,
        "board_name": result.get("name") if isinstance(result, dict) else None,
        "message": f"Successfully retrieved board details for action {id_action}"
    }

@mcp.tool(
    "TRELLO_GET_ACTIONS_BOARD_BY_ID_ACTION_BY_FIELD",
    description="Get action's board field. Retrieves a specified `field` from the trello board associated with the provided trello `idaction`. Use 'all' to get all fields.",
)
def TRELLO_GET_ACTIONS_BOARD_BY_ID_ACTION_BY_FIELD(
    id_action: Annotated[str, "The ID of the action to get the board field for."],
    field: Annotated[str, "The field name to retrieve from the board. Use 'all' to get all fields."]
):
    """Get action's board field. Retrieves a specified `field` from the trello board associated with the provided trello `idaction`. Use 'all' to get all fields."""
    err = _validate_required({"id_action": id_action, "field": field}, ["id_action", "field"])
    if err:
        return err
    
    # Handle special case for "all" field
    if field.lower() == "all":
        endpoint = f"/actions/{id_action}/board"
        result = trello_request("GET", endpoint)
        
        return {
            "successful": True,
            "data": result,
            "action": "get_all_board_fields_by_action_id",
            "action_id": id_action,
            "field": "all",
            "available_fields": list(result.keys()) if isinstance(result, dict) else [],
            "message": f"Successfully retrieved all fields from board associated with action {id_action}"
        }
    else:
        # Handle specific field
        endpoint = f"/actions/{id_action}/board/{field}"
        result = trello_request("GET", endpoint)
        
        return {
            "successful": True,
            "data": result,
            "action": "get_board_field_by_action_id",
            "action_id": id_action,
            "field": field,
            "field_value": result,
            "message": f"Successfully retrieved field '{field}' from board associated with action {id_action}"
        }

@mcp.tool(
    "TRELLO_GET_ACTIONS_BY_ID_ACTION",
    description="Get action by ID. Retrieves detailed information about a specific trello action by its id.",
)
def TRELLO_GET_ACTIONS_BY_ID_ACTION(
    id_action: Annotated[str, "The ID of the action to retrieve."],
    fields: Annotated[str, "Fields to return. Defaults to all."] = "",
    display: Annotated[str, "Display format for the action."] = "",
    entities: Annotated[str, "Entities to include in the response."] = "",
    member: Annotated[str, "Member information to include."] = "",
    member_creator: Annotated[str, "Member creator information to include."] = "",
    member_creator_fields: Annotated[str, "Member creator fields. Defaults to avatarHash, fullName, initials and username."] = "",
    member_fields: Annotated[str, "Member fields. Defaults to avatarHash, fullName, initials and username."] = ""
):
    """Get action by ID. Retrieves detailed information about a specific trello action by its id."""
    err = _validate_required({"id_action": id_action}, ["id_action"])
    if err:
        return err
    
    endpoint = f"/actions/{id_action}"
    params = {}
    
    # Add optional parameters if provided (non-empty strings)
    if fields and fields.strip():
        params["fields"] = fields
    if display and display.strip():
        params["display"] = display
    if entities and entities.strip():
        params["entities"] = entities
    if member and member.strip():
        params["member"] = member
    if member_creator and member_creator.strip():
        params["memberCreator"] = member_creator
    if member_creator_fields and member_creator_fields.strip():
        params["memberCreator_fields"] = member_creator_fields
    if member_fields and member_fields.strip():
        params["member_fields"] = member_fields
    
    result = trello_request("GET", endpoint, params=params)
    
    return {
        "successful": True,
        "data": result,
        "action": "get_action_by_id",
        "action_id": id_action,
        "action_type": result.get("type") if isinstance(result, dict) else None,
        "action_date": result.get("date") if isinstance(result, dict) else None,
        "message": f"Successfully retrieved action {id_action}"
    }

@mcp.tool(
    "TRELLO_GET_ACTIONS_BY_ID_ACTION_BY_FIELD",
    description="Get action field by id. Retrieves the value of a specific field (e.g., 'data', 'date', 'type') from a trello action using its unique id. Use 'all' to get all fields.",
)
def TRELLO_GET_ACTIONS_BY_ID_ACTION_BY_FIELD(
    id_action: Annotated[str, "The ID of the action to get the field from."],
    field: Annotated[str, "The field name to retrieve from the action. Use 'all' to get all fields."]
):
    """Get action field by id. Retrieves the value of a specific field (e.g., 'data', 'date', 'type') from a trello action using its unique id. Use 'all' to get all fields."""
    err = _validate_required({"id_action": id_action, "field": field}, ["id_action", "field"])
    if err:
        return err
    
    # Handle special case for "all" field
    if field.lower() == "all":
        endpoint = f"/actions/{id_action}"
        result = trello_request("GET", endpoint)
        
        return {
            "successful": True,
            "data": result,
            "action": "get_all_action_fields_by_id",
            "action_id": id_action,
            "field": "all",
            "available_fields": list(result.keys()) if isinstance(result, dict) else [],
            "message": f"Successfully retrieved all fields from action {id_action}"
        }
    else:
        # Handle specific field
        endpoint = f"/actions/{id_action}/{field}"
        result = trello_request("GET", endpoint)
        
        return {
            "successful": True,
            "data": result,
            "action": "get_action_field",
            "action_id": id_action,
            "field": field,
            "field_value": result,
            "message": f"Successfully retrieved field '{field}' from action {id_action}"
        }

@mcp.tool(
    "TRELLO_GET_ACTIONS_CARD_BY_ID_ACTION",
    description="Get card by action ID. Retrieves trello card details for a given idaction, which must be an action specifically linked to a card; returns only card data, not action details.",
)
def TRELLO_GET_ACTIONS_CARD_BY_ID_ACTION(
    id_action: Annotated[str, "The ID of the action to get the card from."],
    fields: Annotated[str, "Comma-separated list of card fields to return. Defaults to all."] = "all"
):
    """Get card by action ID. Retrieves trello card details for a given idaction, which must be an action specifically linked to a card; returns only card data, not action details."""
    err = _validate_required({"id_action": id_action}, ["id_action"])
    if err:
        return err
    
    # Build parameters
    params = {}
    if fields and fields.strip() and fields.lower() != "all":
        params["fields"] = fields
    
    endpoint = f"/actions/{id_action}/card"
    result = trello_request("GET", endpoint, params=params)
    
    return {
        "successful": True,
        "data": result,
        "action": "get_card_by_action_id",
        "action_id": id_action,
        "fields": fields,
        "card_id": result.get("id") if isinstance(result, dict) else None,
        "card_name": result.get("name") if isinstance(result, dict) else None,
        "card_url": result.get("url") if isinstance(result, dict) else None,
        "message": f"Successfully retrieved card from action {id_action}"
    }

@mcp.tool(
    "TRELLO_GET_ACTIONS_CARD_BY_ID_ACTION_BY_FIELD",
    description="Get action's card field. Retrieves a specific field from the trello card associated with the given action id. Use 'all' to get all fields.",
)
def TRELLO_GET_ACTIONS_CARD_BY_ID_ACTION_BY_FIELD(
    id_action: Annotated[str, "The ID of the action to get the card field from."],
    field: Annotated[str, "The field name to retrieve from the card. Use 'all' to get all fields."]
):
    """Get action's card field. Retrieves a specific field from the trello card associated with the given action id. Use 'all' to get all fields."""
    err = _validate_required({"id_action": id_action, "field": field}, ["id_action", "field"])
    if err:
        return err
    
    # Handle special case for "all" field
    if field.lower() == "all":
        endpoint = f"/actions/{id_action}/card"
        result = trello_request("GET", endpoint)
        
        return {
            "successful": True,
            "data": result,
            "action": "get_all_card_fields_by_action_id",
            "action_id": id_action,
            "field": "all",
            "available_fields": list(result.keys()) if isinstance(result, dict) else [],
            "message": f"Successfully retrieved all fields from card associated with action {id_action}"
        }
    else:
        # Handle specific field
        endpoint = f"/actions/{id_action}/card/{field}"
        result = trello_request("GET", endpoint)
        
        return {
            "successful": True,
            "data": result,
            "action": "get_card_field_by_action_id",
            "action_id": id_action,
            "field": field,
            "field_value": result,
            "message": f"Successfully retrieved field '{field}' from card associated with action {id_action}"
        }

@mcp.tool(
    "TRELLO_GET_ACTIONS_DISPLAY_BY_ID_ACTION",
    description="Get action display by ID. Retrieves a display-friendly representation of an existing and accessible trello action for ui/report purposes, providing presentation-focused data instead of full raw details and without altering the action.",
)
def TRELLO_GET_ACTIONS_DISPLAY_BY_ID_ACTION(
    id_action: Annotated[str, "The ID of the action to get the display representation for."]
):
    """Get action display by ID. Retrieves a display-friendly representation of an existing and accessible trello action for ui/report purposes, providing presentation-focused data instead of full raw details and without altering the action."""
    err = _validate_required({"id_action": id_action}, ["id_action"])
    if err:
        return err
    
    endpoint = f"/actions/{id_action}/display"
    result = trello_request("GET", endpoint)
    
    return {
        "successful": True,
        "data": result,
        "action": "get_action_display_by_id",
        "action_id": id_action,
        "display_type": result.get("type") if isinstance(result, dict) else None,
        "display_text": result.get("text") if isinstance(result, dict) else None,
        "display_entities": result.get("entities") if isinstance(result, dict) else None,
        "message": f"Successfully retrieved display representation for action {id_action}"
        }

@mcp.tool(
    "TRELLO_GET_ACTIONS_ENTITIES_BY_ID_ACTION",
    description="Get action entities by id. Retrieves all entities (e.g., boards, lists, cards, members) associated with a specific, existing trello action id.",
)
def TRELLO_GET_ACTIONS_ENTITIES_BY_ID_ACTION(
    id_action: Annotated[str, "The ID of the action to get the entities for."]
):
    """Get action entities by id. Retrieves all entities (e.g., boards, lists, cards, members) associated with a specific, existing trello action id."""
    err = _validate_required({"id_action": id_action}, ["id_action"])
    if err:
        return err
    
    endpoint = f"/actions/{id_action}/entities"
    result = trello_request("GET", endpoint)
    
    return {
        "successful": True,
        "data": result,
        "action": "get_action_entities_by_id",
        "action_id": id_action,
        "entities_count": len(result) if isinstance(result, list) else 0,
        "entity_types": list(set([item.get("type") for item in result if isinstance(item, dict) and "type" in item])) if isinstance(result, list) else [],
        "message": f"Successfully retrieved entities for action {id_action}"
        }

@mcp.tool(
    "TRELLO_GET_ACTIONS_LIST_BY_ID_ACTION",
    description="Get an action's list. Retrieves the trello list associated with a specific trello action id, for actions linked to a list.",
)
def TRELLO_GET_ACTIONS_LIST_BY_ID_ACTION(
    id_action: Annotated[str, "The ID of the action to get the list from."],
    fields: Annotated[str, "Comma-separated list of list fields to return. Defaults to all."] = "all"
):
    """Get an action's list. Retrieves the trello list associated with a specific trello action id, for actions linked to a list."""
    err = _validate_required({"id_action": id_action}, ["id_action"])
    if err:
        return err
    
    # Build parameters
    params = {}
    if fields and fields.strip() and fields.lower() != "all":
        params["fields"] = fields
    
    endpoint = f"/actions/{id_action}/list"
    result = trello_request("GET", endpoint, params=params)
    
    return {
        "successful": True,
        "data": result,
        "action": "get_list_by_action_id",
        "action_id": id_action,
        "fields": fields,
        "list_id": result.get("id") if isinstance(result, dict) else None,
        "list_name": result.get("name") if isinstance(result, dict) else None,
        "list_closed": result.get("closed") if isinstance(result, dict) else None,
        "list_id_board": result.get("idBoard") if isinstance(result, dict) else None,
        "message": f"Successfully retrieved list from action {id_action}"
        }

@mcp.tool(
    "TRELLO_GET_ACTIONS_LIST_BY_ID_ACTION_BY_FIELD",
    description="Get field of action's list. Retrieves a specific field of the list associated with a trello action, returning only that single field's value. Use 'all' to get all fields.",
)
def TRELLO_GET_ACTIONS_LIST_BY_ID_ACTION_BY_FIELD(
    id_action: Annotated[str, "The ID of the action to get the list field from."],
    field: Annotated[str, "The field name to retrieve from the list. Use 'all' to get all fields."]
):
    """Get field of action's list. Retrieves a specific field of the list associated with a trello action, returning only that single field's value. Use 'all' to get all fields."""
    err = _validate_required({"id_action": id_action, "field": field}, ["id_action", "field"])
    if err:
        return err
    
    # Handle special case for "all" field
    if field.lower() == "all":
        endpoint = f"/actions/{id_action}/list"
        result = trello_request("GET", endpoint)
        
        return {
            "successful": True,
            "data": result,
            "action": "get_all_list_fields_by_action_id",
            "action_id": id_action,
            "field": "all",
            "available_fields": list(result.keys()) if isinstance(result, dict) else [],
            "message": f"Successfully retrieved all fields from list associated with action {id_action}"
        }
    else:
        # Handle specific field
        endpoint = f"/actions/{id_action}/list/{field}"
        result = trello_request("GET", endpoint)
        
        return {
            "successful": True,
            "data": result,
            "action": "get_list_field_by_action_id",
            "action_id": id_action,
            "field": field,
            "field_value": result,
            "message": f"Successfully retrieved field '{field}' from list associated with action {id_action}"
        }

@mcp.tool(
    "TRELLO_GET_ACTIONS_MEMBER_BY_ID_ACTION",
    description="Get action's member by id. Retrieves specified details of the trello member who performed the action identified by idaction; information is specific to this action's context, not the member's full profile.",
)
def TRELLO_GET_ACTIONS_MEMBER_BY_ID_ACTION(
    id_action: Annotated[str, "The ID of the action to get the member from."],
    fields: Annotated[str, "Comma-separated list of member fields to return. Defaults to all."] = "all"
):
    """Get action's member by id. Retrieves specified details of the trello member who performed the action identified by idaction; information is specific to this action's context, not the member's full profile."""
    err = _validate_required({"id_action": id_action}, ["id_action"])
    if err:
        return err
    
    # First get the action to extract member information
    action_endpoint = f"/actions/{id_action}"
    action_result = trello_request("GET", action_endpoint)
    
    if not isinstance(action_result, dict):
        return {
            "successful": False,
            "error": "Invalid action data received",
            "action": "get_member_by_action_id",
            "action_id": id_action,
            "message": f"Failed to retrieve action {id_action}"
        }
    
    # Extract member information from the action
    member_data = action_result.get("memberCreator", {})
    
    if not member_data:
        return {
            "successful": False,
            "error": "No member information found for this action",
            "action": "get_member_by_action_id",
            "action_id": id_action,
            "message": f"Action {id_action} does not have associated member information"
        }
    
    # Filter fields if specific fields are requested
    if fields and fields.strip() and fields.lower() != "all":
        field_list = [f.strip() for f in fields.split(",")]
        filtered_member = {k: v for k, v in member_data.items() if k in field_list}
    else:
        filtered_member = member_data
    
    return {
        "successful": True,
        "data": filtered_member,
        "action": "get_member_by_action_id",
        "action_id": id_action,
        "fields": fields,
        "member_id": member_data.get("id"),
        "member_username": member_data.get("username"),
        "member_full_name": member_data.get("fullName"),
        "member_avatar_hash": member_data.get("avatarHash"),
        "message": f"Successfully retrieved member from action {id_action}"
        }

@mcp.tool(
    "TRELLO_GET_ACTIONS_MEMBER_BY_ID_ACTION_BY_FIELD",
    description="Get member action field by ID. Fetches a specific field of a member for a trello action, returning only one field per call for optimized data retrieval. Use 'all' to get all fields.",
)
def TRELLO_GET_ACTIONS_MEMBER_BY_ID_ACTION_BY_FIELD(
    id_action: Annotated[str, "The ID of the action to get the member field from."],
    field: Annotated[str, "The field name to retrieve from the member. Use 'all' to get all fields."]
):
    """Get member action field by ID. Fetches a specific field of a member for a trello action, returning only one field per call for optimized data retrieval. Use 'all' to get all fields."""
    err = _validate_required({"id_action": id_action, "field": field}, ["id_action", "field"])
    if err:
        return err
    
    # First get the action to extract member information
    action_endpoint = f"/actions/{id_action}"
    action_result = trello_request("GET", action_endpoint)
    
    if not isinstance(action_result, dict):
        return {
            "successful": False,
            "error": "Invalid action data received",
            "action": "get_member_field_by_action_id",
            "action_id": id_action,
            "field": field,
            "message": f"Failed to retrieve action {id_action}"
        }
    
    # Extract member information from the action
    member_data = action_result.get("memberCreator", {})
    
    if not member_data:
        return {
            "successful": False,
            "error": "No member information found for this action",
            "action": "get_member_field_by_action_id",
            "action_id": id_action,
            "field": field,
            "message": f"Action {id_action} does not have associated member information"
        }
    
    # Handle special case for "all" field
    if field.lower() == "all":
        return {
            "successful": True,
            "data": member_data,
            "action": "get_all_member_fields_by_action_id",
            "action_id": id_action,
            "field": "all",
            "available_fields": list(member_data.keys()) if isinstance(member_data, dict) else [],
            "message": f"Successfully retrieved all fields from member associated with action {id_action}"
        }
    else:
        # Handle specific field
        field_value = member_data.get(field)
        
        if field_value is None:
            return {
                "successful": False,
                "error": f"Field '{field}' not found in member data",
                "action": "get_member_field_by_action_id",
                "action_id": id_action,
                "field": field,
                "available_fields": list(member_data.keys()) if isinstance(member_data, dict) else [],
                "message": f"Field '{field}' not available for member in action {id_action}"
            }
        
        return {
            "successful": True,
            "data": field_value,
            "action": "get_member_field_by_action_id",
            "action_id": id_action,
            "field": field,
            "field_value": field_value,
            "message": f"Successfully retrieved field '{field}' from member associated with action {id_action}"
        }

@mcp.tool(
    "TRELLO_GET_ACTIONS_MEMBER_CREATOR_BY_ID_ACTION",
    description="Fetch action member creator. Retrieves details about the trello member who created the action with the given idaction.",
)
def TRELLO_GET_ACTIONS_MEMBER_CREATOR_BY_ID_ACTION(
    id_action: Annotated[str, "The ID of the action to get the member creator from."],
    fields: Annotated[str, "Comma-separated list of member fields to return. Defaults to all."] = "all"
):
    """Fetch action member creator. Retrieves details about the trello member who created the action with the given idaction."""
    err = _validate_required({"id_action": id_action}, ["id_action"])
    if err:
        return err
    
    # First get the action to extract member creator information
    action_endpoint = f"/actions/{id_action}"
    action_result = trello_request("GET", action_endpoint)
    
    if not isinstance(action_result, dict):
        return {
            "successful": False,
            "error": "Invalid action data received",
            "action": "get_member_creator_by_action_id",
            "action_id": id_action,
            "message": f"Failed to retrieve action {id_action}"
        }
    
    # Extract member creator information from the action
    member_creator_data = action_result.get("memberCreator", {})
    
    if not member_creator_data:
        return {
            "successful": False,
            "error": "No member creator information found for this action",
            "action": "get_member_creator_by_action_id",
            "action_id": id_action,
            "message": f"Action {id_action} does not have associated member creator information"
        }
    
    # Filter fields if specific fields are requested
    if fields and fields.strip() and fields.lower() != "all":
        field_list = [f.strip() for f in fields.split(",")]
        filtered_member = {k: v for k, v in member_creator_data.items() if k in field_list}
    else:
        filtered_member = member_creator_data
    
    return {
        "successful": True,
        "data": filtered_member,
        "action": "get_member_creator_by_action_id",
        "action_id": id_action,
        "fields": fields,
        "member_creator_id": member_creator_data.get("id"),
        "member_creator_username": member_creator_data.get("username"),
        "member_creator_full_name": member_creator_data.get("fullName"),
        "member_creator_avatar_hash": member_creator_data.get("avatarHash"),
        "message": f"Successfully retrieved member creator from action {id_action}"
    }


# -------------------- MAIN --------------------

if __name__ == "__main__":
    mcp.run()
