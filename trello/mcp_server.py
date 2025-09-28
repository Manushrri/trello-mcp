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
    "TRELLO_LIST_CREATE_LIST",
    description="Add new list to board. Deprecated: use 'add lists' instead. creates a new list on a trello board, optionally copying an existing list, setting position, and initial state; does not modify existing lists or move cards.",
)
def TRELLO_LIST_CREATE_LIST(
    id_board: Annotated[str, "The ID of the board to create the list on."],
    name: Annotated[str, "The name of the list to create."],
    id_list_source: Annotated[Optional[str], "The ID of an existing list to copy from."] = None,
    pos: Annotated[Optional[str], "Position of the list (top, bottom, or a number)."] = None,
    closed: Annotated[Optional[str], "Whether the list should be closed/archived (true/false)."] = None,
    subscribed: Annotated[Optional[str], "Whether the user should be subscribed to the list (true/false)."] = None
):
    """Add new list to board. Deprecated: use 'add lists' instead. creates a new list on a trello board, optionally copying an existing list, setting position, and initial state; does not modify existing lists or move cards."""
    # This is a deprecated wrapper around TRELLO_ADD_LISTS
    return TRELLO_ADD_LISTS(
        id_board=id_board,
        name=name,
        id_list_source=id_list_source,
        pos=pos,
        closed=closed,
        subscribed=subscribed
    )





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
    "TRELLO_TRELLO_UPDATE_MEMBER_BOARD_STAR",
    description="Update Member Board Star. Updates an existing board star for a member, allowing changes to the target board (must be a valid, accessible board id if specified) or the star's position.",
)
def TRELLO_TRELLO_UPDATE_MEMBER_BOARD_STAR(
    id_member: Annotated[str, "The ID of the member who owns the board star."],
    id_board_star: Annotated[str, "The ID of the board star to update."],
    id_board: Annotated[str | None, "The ID of the new target board (must be a valid, accessible board id if specified)."] = None,
    pos: Annotated[str | None, "The new position for the board star."] = None
):
    """Update Member Board Star. Updates an existing board star for a member, allowing changes to the target board (must be a valid, accessible board id if specified) or the star's position."""
    err = _validate_required({"id_member": id_member, "id_board_star": id_board_star}, ["id_member", "id_board_star"])
    if err:
        return err
    
    try:
        endpoint = f"/members/{id_member}/boardStars/{id_board_star}"
        
        # Build data payload
        data = {}
        if id_board is not None:
            data["idBoard"] = id_board
        if pos is not None:
            data["pos"] = pos
        
        # Make sure we have something to update
        if not data:
            return {
                "successful": False,
                "error": "No update parameters provided",
                "action": "update_board_star",
                "member_id": id_member,
                "board_star_id": id_board_star,
                "message": "Must provide either id_board or pos to update"
            }
        
        result = trello_request("PUT", endpoint, data=data)
        
        return {
            "successful": True,
            "data": result,
            "action": "update_board_star",
            "member_id": id_member,
            "board_star_id": id_board_star,
            "updated_board_id": id_board,
            "updated_position": pos,
            "message": f"Successfully updated board star {id_board_star} for member {id_member}"
        }
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to update board star: {str(e)}",
            "action": "update_board_star",
            "member_id": id_member,
            "board_star_id": id_board_star,
            "message": f"Failed to update board star {id_board_star} for member {id_member}"
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
    "TRELLO_MARK_CARD_NOTIFICATIONS_READ",
    description="Mark card notifications read. Marks all notifications associated with a specific trello card as read; this is irreversible and only affects read status, not deleting or modifying notifications. Note: This uses a workaround since Trello API doesn't have a direct card-specific endpoint.",
)
def TRELLO_MARK_CARD_NOTIFICATIONS_READ(
    id_card: Annotated[str, "The ID of the card to mark notifications as read for."]
):
    """Mark card notifications read. Marks all notifications associated with a specific trello card as read; this is irreversible and only affects read status, not deleting or modifying notifications. Note: This uses a workaround since Trello API doesn't have a direct card-specific endpoint."""
    err = _validate_required({"id_card": id_card}, ["id_card"])
    if err:
        return err
    
    try:
        # Since Trello API doesn't have a direct endpoint for marking card-specific notifications as read,
        # we'll use the workaround of marking all notifications as read
        # This is the only available option in the Trello API
        endpoint = "/notifications/all/read"
        
        result = trello_request("POST", endpoint)
        
        return {
            "successful": True,
            "data": result,
            "action": "mark_card_notifications_read",
            "card_id": id_card,
            "message": f"Marked all notifications as read (Trello API limitation: no card-specific endpoint available)",
            "note": "Due to Trello API limitations, this marks ALL notifications as read, not just those for the specified card"
        }
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to mark notifications as read: {str(e)}",
            "action": "mark_card_notifications_read",
            "card_id": id_card,
            "message": f"Failed to mark notifications as read"
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
    
    # Get the token from environment variables
    token = get_env("TRELLO_API_TOKEN")
    if not token:
        return {
            "successful": False,
            "error": "TRELLO_API_TOKEN environment variable not set",
            "action": "create_webhook",
            "message": "Failed to create webhook: No API token available"
        }
    
    endpoint = f"/tokens/{token}/webhooks"
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
    "TRELLO_UPDATE_ACTIONS_BY_ID_ACTION",
    description="Update action text. Updates the `text` field of a specific trello comment action, identified by `idaction`. Note: Only comment actions can be edited - other action types cannot be modified.",
)
def TRELLO_UPDATE_ACTIONS_BY_ID_ACTION(
    id_action: Annotated[str, "The ID of the action to update."],
    text: Annotated[str, "The new text content for the action."]
):
    """Update action text. Updates the `text` field of a specific trello comment action, identified by `idaction`. Note: Only comment actions can be edited - other action types cannot be modified."""
    err = _validate_required({"id_action": id_action, "text": text}, ["id_action", "text"])
    if err:
        return err
    
    try:
        endpoint = f"/actions/{id_action}"
        
        # Build data payload
        data = {
            "text": text
        }
        
        result = trello_request("PUT", endpoint, data=data)
        
        return {
            "successful": True,
            "data": result,
            "action": "update_action_text",
            "action_id": id_action,
            "updated_text": text,
            "message": f"Successfully updated action {id_action} text"
        }
    except Exception as e:
        error_message = str(e)
        
        # Provide specific guidance for common errors
        if "403" in error_message and "can't be edited" in error_message:
            return {
                "successful": False,
                "error": f"Action cannot be edited: {error_message}",
                "action": "update_action_text",
                "action_id": id_action,
                "message": f"Failed to update action {id_action} text - this action type cannot be edited",
                "guidance": "Only comment actions can typically be edited. Other action types (like card moves, label changes, etc.) cannot be modified after creation.",
                "suggestion": "Use TRELLO_GET_ACTIONS_BY_ID_ACTION to check the action type first, or create a new comment action instead."
            }
        elif "404" in error_message:
            return {
                "successful": False,
                "error": f"Action not found: {error_message}",
                "action": "update_action_text",
                "action_id": id_action,
                "message": f"Failed to update action {id_action} text - action not found",
                "guidance": "The action ID may be invalid or the action may have been deleted.",
                "suggestion": "Verify the action ID is correct and the action still exists."
            }
        else:
            return {
                "successful": False,
                "error": f"Failed to update action text: {error_message}",
                "action": "update_action_text",
                "action_id": id_action,
                "message": f"Failed to update action {id_action} text"
            }


@mcp.tool(
    "TRELLO_UPDATE_ACTIONS_TEXT_BY_ID_ACTION",
    description="Update action text. Updates the text of an existing trello action (e.g., a comment or card update) identified by `idaction`; this change only affects the action's text content. Note: Only comment actions can be edited - other action types cannot be modified.",
)
def TRELLO_UPDATE_ACTIONS_TEXT_BY_ID_ACTION(
    id_action: Annotated[str, "The ID of the action to update."],
    value: Annotated[str, "The new text content for the action."]
):
    """Update action text. Updates the text of an existing trello action (e.g., a comment or card update) identified by `idaction`; this change only affects the action's text content. Note: Only comment actions can be edited - other action types cannot be modified."""
    err = _validate_required({"id_action": id_action, "value": value}, ["id_action", "value"])
    if err:
        return err
    
    try:
        endpoint = f"/actions/{id_action}"
        
        # Build data payload
        data = {
            "text": value
        }
        
        result = trello_request("PUT", endpoint, data=data)
        
        return {
            "successful": True,
            "data": result,
            "action": "update_action_text",
            "action_id": id_action,
            "updated_text": value,
            "message": f"Successfully updated action {id_action} text"
        }
    except Exception as e:
        error_message = str(e)
        
        # Provide specific guidance for common errors
        if "403" in error_message and "can't be edited" in error_message:
            return {
                "successful": False,
                "error": f"Action cannot be edited: {error_message}",
                "action": "update_action_text",
                "action_id": id_action,
                "message": f"Failed to update action {id_action} text - this action type cannot be edited",
                "guidance": "Only comment actions can typically be edited. Other action types (like card moves, label changes, etc.) cannot be modified after creation.",
                "suggestion": "Use TRELLO_GET_ACTIONS_BY_ID_ACTION to check the action type first, or create a new comment action instead."
            }
        elif "404" in error_message:
            return {
                "successful": False,
                "error": f"Action not found: {error_message}",
                "action": "update_action_text",
                "action_id": id_action,
                "message": f"Failed to update action {id_action} text - action not found",
                "guidance": "The action ID may be invalid or the action may have been deleted.",
                "suggestion": "Verify the action ID is correct and the action still exists."
            }
        else:
            return {
                "successful": False,
                "error": f"Failed to update action text: {error_message}",
                "action": "update_action_text",
                "action_id": id_action,
                "message": f"Failed to update action {id_action} text"
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

@mcp.tool(
    "TRELLO_GET_ACTIONS_MEMBER_CREATOR_BY_ID_ACTION_BY_FIELD",
    description="Get action member creator field. Gets information about the creator of a trello action.",
)
def TRELLO_GET_ACTIONS_MEMBER_CREATOR_BY_ID_ACTION_BY_FIELD(
    id_action: Annotated[str, "The ID of the action to get the member creator field from."],
    field: Annotated[str, "The specific field to retrieve from the member creator."]
):
    """Get action member creator field. Gets information about the creator of a trello action."""
    err = _validate_required({"id_action": id_action, "field": field}, ["id_action", "field"])
    if err:
        return err
    
    # First get the action to extract member creator information
    action_endpoint = f"/actions/{id_action}"
    action_result = trello_request("GET", action_endpoint)
    
    if not isinstance(action_result, dict):
        return {
            "successful": False,
            "error": "Invalid action data received",
            "action": "get_member_creator_field_by_action_id",
            "action_id": id_action,
            "field": field,
            "message": f"Failed to retrieve action {id_action}"
        }
    
    # Extract member creator information from the action
    member_creator_data = action_result.get("memberCreator", {})
    
    if not member_creator_data:
        return {
            "successful": False,
            "error": "No member creator information found for this action",
            "action": "get_member_creator_field_by_action_id",
            "action_id": id_action,
            "field": field,
            "message": f"Action {id_action} does not have associated member creator information"
        }
    
    # Handle "all" field request
    if field.lower() == "all":
        return {
            "successful": True,
            "data": member_creator_data,
            "action": "get_member_creator_field_by_action_id",
            "action_id": id_action,
            "field": field,
            "member_creator_id": member_creator_data.get("id"),
            "member_creator_username": member_creator_data.get("username"),
            "member_creator_full_name": member_creator_data.get("fullName"),
            "member_creator_avatar_hash": member_creator_data.get("avatarHash"),
            "message": f"Successfully retrieved all fields from member creator of action {id_action}"
        }
    
    # Get the specific field value
    field_value = member_creator_data.get(field)
    
    if field_value is None:
        return {
            "successful": False,
            "error": f"Field '{field}' not found in member creator data",
            "action": "get_member_creator_field_by_action_id",
            "action_id": id_action,
            "field": field,
            "available_fields": list(member_creator_data.keys()),
            "message": f"Field '{field}' not available for member creator of action {id_action}"
        }
    
    return {
        "successful": True,
        "data": {field: field_value},
        "action": "get_member_creator_field_by_action_id",
        "action_id": id_action,
        "field": field,
        "field_value": field_value,
        "member_creator_id": member_creator_data.get("id"),
        "message": f"Successfully retrieved field '{field}' from member creator of action {id_action}"
    }

@mcp.tool(
    "TRELLO_GET_ACTIONS_ORGANIZATION_BY_ID_ACTION",
    description="Fetch organization action by id. Fetches the organization details for a given trello action, if the action has an associated organization.",
)
def TRELLO_GET_ACTIONS_ORGANIZATION_BY_ID_ACTION(
    id_action: Annotated[str, "The ID of the action to get the organization from."],
    fields: Annotated[str, "Comma-separated list of organization fields to return. Defaults to all."] = "all"
):
    """Fetch organization action by id. Fetches the organization details for a given trello action, if the action has an associated organization."""
    err = _validate_required({"id_action": id_action}, ["id_action"])
    if err:
        return err
    
    # First get the action to extract organization information
    action_endpoint = f"/actions/{id_action}"
    action_result = trello_request("GET", action_endpoint)
    
    if not isinstance(action_result, dict):
        return {
            "successful": False,
            "error": "Invalid action data received",
            "action": "get_organization_by_action_id",
            "action_id": id_action,
            "message": f"Failed to retrieve action {id_action}"
        }
    
    # Extract organization information from the action
    organization_data = action_result.get("organization", {})
    
    if not organization_data:
        return {
            "successful": False,
            "error": "No organization information found for this action",
            "action": "get_organization_by_action_id",
            "action_id": id_action,
            "message": f"Action {id_action} does not have associated organization information"
        }
    
    # Filter fields if specific fields are requested
    if fields and fields.strip() and fields.lower() != "all":
        field_list = [f.strip() for f in fields.split(",")]
        filtered_organization = {k: v for k, v in organization_data.items() if k in field_list}
    else:
        filtered_organization = organization_data
    
    return {
        "successful": True,
        "data": filtered_organization,
        "action": "get_organization_by_action_id",
        "action_id": id_action,
        "fields": fields,
        "organization_id": organization_data.get("id"),
        "organization_name": organization_data.get("name"),
        "organization_display_name": organization_data.get("displayName"),
        "message": f"Successfully retrieved organization from action {id_action}"
    }

@mcp.tool(
    "TRELLO_GET_ACTIONS_ORGANIZATION_BY_ID_ACTION_BY_FIELD",
    description="Get action's organization field. Retrieves the value of a specific field for the organization associated with a trello idaction; use if the action has an organization and you need only that field (e.g., 'name', 'id', 'url').",
)
def TRELLO_GET_ACTIONS_ORGANIZATION_BY_ID_ACTION_BY_FIELD(
    id_action: Annotated[str, "The ID of the action to get the organization field from."],
    field: Annotated[str, "The specific field to retrieve from the organization."]
):
    """Get action's organization field. Retrieves the value of a specific field for the organization associated with a trello idaction; use if the action has an organization and you need only that field (e.g., 'name', 'id', 'url')."""
    err = _validate_required({"id_action": id_action, "field": field}, ["id_action", "field"])
    if err:
        return err
    
    # First get the action to extract organization information
    action_endpoint = f"/actions/{id_action}"
    action_result = trello_request("GET", action_endpoint)
    
    if not isinstance(action_result, dict):
        return {
            "successful": False,
            "error": "Invalid action data received",
            "action": "get_organization_field_by_action_id",
            "action_id": id_action,
            "field": field,
            "message": f"Failed to retrieve action {id_action}"
        }
    
    # Extract organization information from the action
    organization_data = action_result.get("organization", {})
    
    if not organization_data:
        return {
            "successful": False,
            "error": "No organization information found for this action",
            "action": "get_organization_field_by_action_id",
            "action_id": id_action,
            "field": field,
            "message": f"Action {id_action} does not have associated organization information"
        }
    
    # Handle "all" field request
    if field.lower() == "all":
        return {
            "successful": True,
            "data": organization_data,
            "action": "get_organization_field_by_action_id",
            "action_id": id_action,
            "field": field,
            "organization_id": organization_data.get("id"),
            "organization_name": organization_data.get("name"),
            "organization_display_name": organization_data.get("displayName"),
            "message": f"Successfully retrieved all fields from organization of action {id_action}"
        }
    
    # Get the specific field value
    field_value = organization_data.get(field)
    
    if field_value is None:
        return {
            "successful": False,
            "error": f"Field '{field}' not found in organization data",
            "action": "get_organization_field_by_action_id",
            "action_id": id_action,
            "field": field,
            "available_fields": list(organization_data.keys()),
            "message": f"Field '{field}' not available for organization of action {id_action}"
        }
    
    return {
        "successful": True,
        "data": {field: field_value},
        "action": "get_organization_field_by_action_id",
        "action_id": id_action,
        "field": field,
        "field_value": field_value,
        "organization_id": organization_data.get("id"),
        "message": f"Successfully retrieved field '{field}' from organization of action {id_action}"
    }

@mcp.tool(
    "TRELLO_GET_BATCH",
    description="Get batch. Executes multiple trello api get requests in a single batch operation for efficient bulk data retrieval.",
)
def TRELLO_GET_BATCH(
    urls: Annotated[str, "Comma-separated list of Trello API URLs to fetch in batch. URLs should be relative paths like '/boards/123', '/cards/456', etc."]
):
    """Get batch. Executes multiple trello api get requests in a single batch operation for efficient bulk data retrieval."""
    err = _validate_required({"urls": urls}, ["urls"])
    if err:
        return err
    
    # Parse URLs from comma-separated string
    url_list = [url.strip() for url in urls.split(",") if url.strip()]
    
    if not url_list:
        return {
            "successful": False,
            "error": "No valid URLs provided",
            "action": "batch_get",
            "message": "Please provide at least one valid URL"
        }
    
    # Validate URLs (should be relative paths starting with /)
    invalid_urls = []
    for url in url_list:
        if not url.startswith('/'):
            invalid_urls.append(url)
    
    if invalid_urls:
        return {
            "successful": False,
            "error": f"Invalid URLs found: {', '.join(invalid_urls)}",
            "action": "batch_get",
            "message": "All URLs must be relative paths starting with '/' (e.g., '/boards/123', '/cards/456')"
        }
    
    # Execute batch requests
    results = {}
    errors = []
    successful_count = 0
    
    for i, url in enumerate(url_list):
        try:
            result = trello_request("GET", url)
            results[f"url_{i+1}"] = {
                "url": url,
                "data": result,
                "success": True
            }
            successful_count += 1
        except Exception as e:
            error_msg = str(e)
            results[f"url_{i+1}"] = {
                "url": url,
                "data": None,
                "success": False,
                "error": error_msg
            }
            errors.append(f"URL {i+1} ({url}): {error_msg}")
    
    # Determine overall success
    overall_success = len(errors) == 0
    
    return {
        "successful": overall_success,
        "data": results,
        "action": "batch_get",
        "total_urls": len(url_list),
        "successful_requests": successful_count,
        "failed_requests": len(errors),
        "errors": errors if errors else None,
        "message": f"Batch operation completed: {successful_count}/{len(url_list)} requests successful"
    }

@mcp.tool(
    "TRELLO_GET_BOARDS_ACTIONS_BY_ID_BOARD",
    description="Get board actions by id. Retrieves actions (e.g., card creations, comments) for a trello board by its id, useful for activity tracking; the board must exist.",
)
def TRELLO_GET_BOARDS_ACTIONS_BY_ID_BOARD(
    id_board: Annotated[str, "The ID of the board to get actions from."],
    before: Annotated[str, "Return actions before this date."] = "",
    display: Annotated[str, "Return display-friendly representation of actions."] = "",
    entities: Annotated[str, "Return entities associated with actions."] = "",
    fields: Annotated[str, "Comma-separated list of action fields to return. Defaults to all."] = "all",
    filter: Annotated[str, "Filter actions by type. Defaults to all."] = "all",
    format: Annotated[str, "Format of the response. Defaults to list."] = "list",
    id_models: Annotated[str, "Comma-separated list of model IDs to filter actions."] = "",
    limit: Annotated[str, "Maximum number of actions to return. Defaults to 50."] = "50",
    member: Annotated[str, "Filter actions by member."] = "",
    member_creator: Annotated[str, "Filter actions by member creator."] = "",
    member_creator_fields: Annotated[str, "Comma-separated list of member creator fields. Defaults to avatarHash, fullName, initials and username."] = "avatarHash,fullName,initials,username",
    member_fields: Annotated[str, "Comma-separated list of member fields. Defaults to avatarHash, fullName, initials and username."] = "avatarHash,fullName,initials,username",
    page: Annotated[str, "Page number for pagination. Defaults to 0."] = "0",
    since: Annotated[str, "Return actions since this date."] = ""
):
    """Get board actions by id. Retrieves actions (e.g., card creations, comments) for a trello board by its id, useful for activity tracking; the board must exist."""
    err = _validate_required({"id_board": id_board}, ["id_board"])
    if err:
        return err
    
    # Build the endpoint
    endpoint = f"/boards/{id_board}/actions"
    
    # Build query parameters
    params = {}
    
    # Add parameters only if they have values
    if before and before.strip():
        params["before"] = before.strip()
    if display and display.strip():
        params["display"] = display.strip()
    if entities and entities.strip():
        params["entities"] = entities.strip()
    if fields and fields.strip() and fields.lower() != "all":
        params["fields"] = fields.strip()
    if filter and filter.strip() and filter.lower() != "all":
        params["filter"] = filter.strip()
    if format and format.strip() and format.lower() != "list":
        params["format"] = format.strip()
    if id_models and id_models.strip():
        params["idModels"] = id_models.strip()
    if limit and limit.strip() and limit != "50":
        params["limit"] = limit.strip()
    if member and member.strip():
        params["member"] = member.strip()
    if member_creator and member_creator.strip():
        params["memberCreator"] = member_creator.strip()
    if member_creator_fields and member_creator_fields.strip() and member_creator_fields != "avatarHash,fullName,initials,username":
        params["memberCreator_fields"] = member_creator_fields.strip()
    if member_fields and member_fields.strip() and member_fields != "avatarHash,fullName,initials,username":
        params["member_fields"] = member_fields.strip()
    if page and page.strip() and page != "0":
        params["page"] = page.strip()
    if since and since.strip():
        params["since"] = since.strip()
    
    # Make the API request
    result = trello_request("GET", endpoint, params=params)
    
    if not isinstance(result, list):
        return {
            "successful": False,
            "error": "Invalid actions data received",
            "action": "get_board_actions",
            "board_id": id_board,
            "message": f"Failed to retrieve actions for board {id_board}"
        }
    
    return {
        "successful": True,
        "data": result,
        "action": "get_board_actions",
        "board_id": id_board,
        "total_actions": len(result),
        "fields": fields,
        "filter": filter,
        "limit": limit,
        "page": page,
        "message": f"Successfully retrieved {len(result)} actions for board {id_board}"
    }

@mcp.tool(
    "TRELLO_GET_BOARDS_STARS_BY_ID_BOARD",
    description="Get board stars by board ID. Retrieves board stars (user-marked favorites) for a specified trello board, where idboard must be an existing board; use to list a user's starred boards or all stars on a particular board.",
)
def TRELLO_GET_BOARDS_STARS_BY_ID_BOARD(
    id_board: Annotated[str, "The ID of the board to get stars from."],
    filter: Annotated[str, "Filter stars by scope. Defaults to mine."] = "mine"
):
    """Get board stars by board ID. Retrieves board stars (user-marked favorites) for a specified trello board, where idboard must be an existing board; use to list a user's starred boards or all stars on a particular board."""
    err = _validate_required({"id_board": id_board}, ["id_board"])
    if err:
        return err
    
    # Build the endpoint
    endpoint = f"/boards/{id_board}/boardStars"
    
    # Build query parameters
    params = {}
    
    # Add filter parameter if not default
    if filter and filter.strip() and filter.lower() != "mine":
        params["filter"] = filter.strip()
    
    # Make the API request
    result = trello_request("GET", endpoint, params=params)
    
    if not isinstance(result, list):
        return {
            "successful": False,
            "error": "Invalid board stars data received",
            "action": "get_board_stars",
            "board_id": id_board,
            "message": f"Failed to retrieve board stars for board {id_board}"
        }
    
    return {
        "successful": True,
        "data": result,
        "action": "get_board_stars",
        "board_id": id_board,
        "total_stars": len(result),
        "filter": filter,
        "message": f"Successfully retrieved {len(result)} board stars for board {id_board}"
    }

@mcp.tool(
    "TRELLO_GET_BOARDS_BOARD_STARS_BY_ID_BOARD",
    description="Get board stars by board ID. Retrieves board stars (user-marked favorites) for a specified trello board, where idboard must be an existing board; use to list a user's starred boards or all stars on a particular board.",
)
def TRELLO_GET_BOARDS_BOARD_STARS_BY_ID_BOARD(
    id_board: Annotated[str, "The ID of the board to get stars from."],
    filter: Annotated[str, "Filter stars by scope. Defaults to mine."] = "mine"
):
    """Get board stars by board ID. Retrieves board stars (user-marked favorites) for a specified trello board, where idboard must be an existing board; use to list a user's starred boards or all stars on a particular board."""
    err = _validate_required({"id_board": id_board}, ["id_board"])
    if err:
        return err
    
    # Build the endpoint
    endpoint = f"/boards/{id_board}/boardStars"
    
    # Build query parameters
    params = {}
    
    # Add filter parameter if not default
    if filter and filter.strip() and filter.lower() != "mine":
        params["filter"] = filter.strip()
    
    # Make the API request
    result = trello_request("GET", endpoint, params=params)
    
    if not isinstance(result, list):
        return {
            "successful": False,
            "error": "Invalid board stars data received",
            "action": "get_board_stars",
            "board_id": id_board,
            "message": f"Failed to retrieve board stars for board {id_board}"
        }
    
    return {
        "successful": True,
        "data": result,
        "action": "get_board_stars",
        "board_id": id_board,
        "total_stars": len(result),
        "filter": filter,
        "message": f"Successfully retrieved {len(result)} board stars for board {id_board}"
    }


@mcp.tool(
    "TRELLO_GET_BOARDS_MEMBERS_INVITED_BY_ID_BOARD",
    description="Get invited board members. Note: Trello API doesn't provide a direct way to get pending invitations. This tool returns current board members and explains the limitation.",
)
def TRELLO_GET_BOARDS_MEMBERS_INVITED_BY_ID_BOARD(
    id_board: Annotated[str, "The ID of the board to get invited members from."],
    fields: Annotated[str, "Comma-separated list of member fields. Defaults to all."] = "all"
):
    """Get invited board members. Note: Trello API doesn't provide a direct way to get pending invitations. This tool returns current board members and explains the limitation."""
    err = _validate_required({"id_board": id_board}, ["id_board"])
    if err:
        return err
    
    try:
        # Get all current board members (invited members only appear after they join)
        members_endpoint = f"/boards/{id_board}/members"
        members_params = {}
        if fields and fields.strip() and fields.lower() != "all":
            members_params["fields"] = fields.strip()
        
        all_members = trello_request("GET", members_endpoint, params=members_params)
        
        if not isinstance(all_members, list):
            return {
                "successful": False,
                "error": "Invalid members data received",
                "action": "get_board_invited_members",
                "board_id": id_board,
                "message": f"Failed to retrieve members from board {id_board}"
            }
        
        return {
            "successful": True,
            "data": all_members,
            "action": "get_board_invited_members",
            "board_id": id_board,
            "member_count": len(all_members),
            "fields": fields,
            "message": f"Retrieved {len(all_members)} current members from board {id_board}",
            "important_note": "Trello API limitation: Invited members only appear in the API after they accept the invitation. Pending invitations are not accessible via API.",
            "explanation": "When you invite someone to a Trello board, they receive an email invitation. They only become visible in the API once they click the invitation link and join the board. There's no API endpoint to see pending invitations."
        }
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve members: {str(e)}",
            "action": "get_board_invited_members",
            "board_id": id_board,
            "message": f"Failed to retrieve members from board {id_board}",
            "important_note": "Trello API limitation: Invited members only appear in the API after they accept the invitation."
        }


@mcp.tool(
    "TRELLO_GET_BOARDS_MEMBERS_INVITED_BY_ID_BOARD_BY_FIELD",
    description="Retrieve invited board member field. Note: Trello API doesn't support getting pending invitations. This tool explains the limitation and returns current board members.",
)
def TRELLO_GET_BOARDS_MEMBERS_INVITED_BY_ID_BOARD_BY_FIELD(
    field: Annotated[str, "The field to retrieve from invited members (e.g., email, username, fullName)."],
    id_board: Annotated[str, "The ID of the board to get invited member fields from."]
):
    """Retrieve invited board member field. Note: Trello API doesn't support getting pending invitations. This tool explains the limitation and returns current board members."""
    err = _validate_required({"field": field, "id_board": id_board}, ["field", "id_board"])
    if err:
        return err
    
    try:
        # Get current board members (invited members only appear after they join)
        endpoint = f"/boards/{id_board}/members"
        
        # Build query parameters
        params = {"fields": field}
        
        # Make the API request
        result = trello_request("GET", endpoint, params=params)
        
        if not isinstance(result, list):
            return {
                "successful": False,
                "error": "Invalid members data received",
                "action": "get_board_invited_member_field",
                "board_id": id_board,
                "field": field,
                "message": f"Failed to retrieve member field '{field}' from board {id_board}"
            }
        
        return {
            "successful": True,
            "data": result,
            "action": "get_board_invited_member_field",
            "board_id": id_board,
            "field": field,
            "member_count": len(result),
            "message": f"Retrieved field '{field}' from {len(result)} current members for board {id_board}",
            "important_note": "TRELLO API LIMITATION: There is no API endpoint to get pending board invitations. Invited members only appear in the API after they accept the invitation.",
            "explanation": "When you invite someone to a Trello board via API or UI, they receive an email invitation. However, Trello's API does not provide any endpoint to see who has been invited but hasn't joined yet. They only become visible in the /boards/{id}/members endpoint after they click the invitation link and join the board.",
            "workaround": "To track invitations, you would need to maintain your own records outside of Trello's API."
        }
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve member field: {str(e)}",
            "action": "get_board_invited_member_field",
            "board_id": id_board,
            "field": field,
            "message": f"Failed to retrieve member field '{field}' from board {id_board}",
            "important_note": "TRELLO API LIMITATION: There is no API endpoint to get pending board invitations."
        }


@mcp.tool(
    "TRELLO_GET_BOARDS_MY_PREFS_BY_ID_BOARD",
    description="Get my board preferences. Retrieves the authenticated user's preferences for a specific trello board.",
)
def TRELLO_GET_BOARDS_MY_PREFS_BY_ID_BOARD(
    id_board: Annotated[str, "The ID of the board to get preferences for."]
):
    """Get my board preferences. Retrieves the authenticated user's preferences for a specific trello board."""
    err = _validate_required({"id_board": id_board}, ["id_board"])
    if err:
        return err
    
    try:
        # Get user's preferences for the board
        endpoint = f"/boards/{id_board}/myPrefs"
        
        # Make the API request
        result = trello_request("GET", endpoint)
        
        if not isinstance(result, dict):
            return {
                "successful": False,
                "error": "Invalid preferences data received",
                "action": "get_board_my_prefs",
                "board_id": id_board,
                "message": f"Failed to retrieve preferences for board {id_board}"
            }
        
        return {
            "successful": True,
            "data": result,
            "action": "get_board_my_prefs",
            "board_id": id_board,
            "message": f"Successfully retrieved preferences for board {id_board}",
            "preferences": result
        }
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve board preferences: {str(e)}",
            "action": "get_board_my_prefs",
            "board_id": id_board,
            "message": f"Failed to retrieve preferences for board {id_board}"
        }


@mcp.tool(
    "TRELLO_GET_BOARDS_ORGANIZATION_BY_ID_BOARD",
    description="Get board organization. Fetches information about the trello workspace (organization) to which a specific board belongs, returning details for the workspace only, not the board itself or its content.",
)
def TRELLO_GET_BOARDS_ORGANIZATION_BY_ID_BOARD(
    id_board: Annotated[str, "The ID of the board to get organization information for."],
    fields: Annotated[str, "The fields to retrieve from the organization (e.g., name, displayName, desc, website). Defaults to all."] = "all"
):
    """Get board organization. Fetches information about the trello workspace (organization) to which a specific board belongs, returning details for the workspace only, not the board itself or its content."""
    err = _validate_required({"id_board": id_board}, ["id_board"])
    if err:
        return err
    
    try:
        # Get organization information for the board
        endpoint = f"/boards/{id_board}/organization"
        
        # Build query parameters
        params = {"fields": fields}
        
        # Make the API request
        result = trello_request("GET", endpoint, params=params)
        
        if not isinstance(result, dict):
            return {
                "successful": False,
                "error": "Invalid organization data received",
                "action": "get_board_organization",
                "board_id": id_board,
                "fields": fields,
                "message": f"Failed to retrieve organization information for board {id_board}"
            }
        
        return {
            "successful": True,
            "data": result,
            "action": "get_board_organization",
            "board_id": id_board,
            "fields": fields,
            "message": f"Successfully retrieved organization information for board {id_board}",
            "organization": result
        }
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve board organization: {str(e)}",
            "action": "get_board_organization",
            "board_id": id_board,
            "fields": fields,
            "message": f"Failed to retrieve organization information for board {id_board}"
        }


@mcp.tool(
    "TRELLO_GET_BOARDS_ORGANIZATION_BY_ID_BOARD_BY_FIELD",
    description="Get board organization field. Retrieves a specific field from the organization associated with a trello board, useful for obtaining targeted details without fetching the entire organization object.",
)
def TRELLO_GET_BOARDS_ORGANIZATION_BY_ID_BOARD_BY_FIELD(
    field: Annotated[str, "The field to retrieve from the organization (e.g., name, displayName, desc, website)."],
    id_board: Annotated[str, "The ID of the board to get organization field from."]
):
    """Get board organization field. Retrieves a specific field from the organization associated with a trello board, useful for obtaining targeted details without fetching the entire organization object."""
    err = _validate_required({"field": field, "id_board": id_board}, ["field", "id_board"])
    if err:
        return err
    
    try:
        # Get specific organization field for the board
        endpoint = f"/boards/{id_board}/organization"
        
        # Build query parameters
        params = {"fields": field}
        
        # Make the API request
        result = trello_request("GET", endpoint, params=params)
        
        if not isinstance(result, dict):
            return {
                "successful": False,
                "error": "Invalid organization field data received",
                "action": "get_board_organization_field",
                "board_id": id_board,
                "field": field,
                "message": f"Failed to retrieve organization field '{field}' for board {id_board}"
            }
        
        return {
            "successful": True,
            "data": result,
            "action": "get_board_organization_field",
            "board_id": id_board,
            "field": field,
            "message": f"Successfully retrieved organization field '{field}' for board {id_board}",
            "organization_field": result
        }
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve board organization field: {str(e)}",
            "action": "get_board_organization_field",
            "board_id": id_board,
            "field": field,
            "message": f"Failed to retrieve organization field '{field}' for board {id_board}"
        }


@mcp.tool(
    "TRELLO_GET_CARDS_ACTIONS_BY_ID_CARD",
    description="Get card actions by id. Retrieves the history of actions (e.g., comments, updates, moves) for a trello card specified by idcard; the card must exist and very old actions might not be available.",
)
def TRELLO_GET_CARDS_ACTIONS_BY_ID_CARD(
    id_card: Annotated[str, "The ID of the card to get actions for."],
    before: Annotated[str | None, "An action ID. Only return actions before this action."] = None,
    display: Annotated[str | None, "The format for the returned actions."] = None,
    entities: Annotated[str | None, "Whether to include entities in the response."] = None,
    fields: Annotated[str, "The fields to retrieve from the actions (e.g., id, type, date, data). Defaults to all."] = "all",
    filter: Annotated[str, "The types of actions to return (e.g., commentCard, updateCard). Defaults to commentCard and updateCard:idList."] = "commentCard,updateCard:idList",
    format: Annotated[str, "The format for the returned actions. Defaults to list."] = "list",
    id_models: Annotated[str | None, "The IDs of models to include in the response."] = None,
    limit: Annotated[str, "The maximum number of actions to return. Defaults to 50."] = "50",
    member: Annotated[str | None, "Whether to include member information."] = None,
    member_creator: Annotated[str | None, "Whether to include member creator information."] = None,
    member_creator_fields: Annotated[str, "The fields to retrieve from member creators. Defaults to avatarHash, fullName, initials and username."] = "avatarHash,fullName,initials,username",
    member_fields: Annotated[str, "The fields to retrieve from members. Defaults to avatarHash, fullName, initials and username."] = "avatarHash,fullName,initials,username",
    page: Annotated[str, "The page of results to return. Defaults to 0."] = "0",
    since: Annotated[str | None, "An action ID. Only return actions after this action."] = None
):
    """Get card actions by id. Retrieves the history of actions (e.g., comments, updates, moves) for a trello card specified by idcard; the card must exist and very old actions might not be available."""
    err = _validate_required({"id_card": id_card}, ["id_card"])
    if err:
        return err
    
    try:
        # Get actions for the card
        endpoint = f"/cards/{id_card}/actions"
        
        # Build query parameters
        params = {}
        if before is not None:
            params["before"] = before
        if display is not None:
            params["display"] = display
        if entities is not None:
            params["entities"] = entities
        if fields is not None:
            params["fields"] = fields
        if filter is not None:
            params["filter"] = filter
        if format is not None:
            params["format"] = format
        if id_models is not None:
            params["idModels"] = id_models
        if limit is not None:
            params["limit"] = limit
        if member is not None:
            params["member"] = member
        if member_creator is not None:
            params["memberCreator"] = member_creator
        if member_creator_fields is not None:
            params["memberCreator_fields"] = member_creator_fields
        if member_fields is not None:
            params["member_fields"] = member_fields
        if page is not None:
            params["page"] = page
        if since is not None:
            params["since"] = since
        
        # Make the API request
        result = trello_request("GET", endpoint, params=params)
        
        if not isinstance(result, list):
            return {
                "successful": False,
                "error": "Invalid actions data received",
                "action": "get_card_actions",
                "card_id": id_card,
                "message": f"Failed to retrieve actions for card {id_card}"
            }
        
        return {
            "successful": True,
            "data": result,
            "action": "get_card_actions",
            "card_id": id_card,
            "actions_count": len(result),
            "message": f"Successfully retrieved {len(result)} actions for card {id_card}",
            "actions": result,
            "note": "Very old actions might not be available due to Trello's data retention policies"
        }
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve card actions: {str(e)}",
            "action": "get_card_actions",
            "card_id": id_card,
            "message": f"Failed to retrieve actions for card {id_card}"
        }


@mcp.tool(
    "TRELLO_GET_CARDS_ATTACHMENTS_BY_ID_CARD",
    description="Get card attachments. Retrieves attachments for a trello card.",
)
def TRELLO_GET_CARDS_ATTACHMENTS_BY_ID_CARD(
    id_card: Annotated[str, "The ID of the card to get attachments for."],
    fields: Annotated[str, "The fields to retrieve from the attachments (e.g., id, name, url, mimeType). Defaults to all."] = "all"
):
    """Get card attachments. Retrieves attachments for a trello card."""
    err = _validate_required({"id_card": id_card}, ["id_card"])
    if err:
        return err
    
    try:
        # Get attachments for the card
        endpoint = f"/cards/{id_card}/attachments"
        
        # Build query parameters
        params = {}
        if fields is not None:
            params["fields"] = fields
        
        # Make the API request
        result = trello_request("GET", endpoint, params=params)
        
        if not isinstance(result, list):
            return {
                "successful": False,
                "error": "Invalid attachments data received",
                "action": "get_card_attachments",
                "card_id": id_card,
                "message": f"Failed to retrieve attachments for card {id_card}"
            }
        
        return {
            "successful": True,
            "data": result,
            "action": "get_card_attachments",
            "card_id": id_card,
            "attachments_count": len(result),
            "message": f"Successfully retrieved {len(result)} attachments for card {id_card}",
            "attachments": result,
            "note": "Filter parameter is not supported by Trello API for attachments. All attachments are returned. Use fields parameter to limit returned data."
        }
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve card attachments: {str(e)}",
            "action": "get_card_attachments",
            "card_id": id_card,
            "message": f"Failed to retrieve attachments for card {id_card}"
        }


@mcp.tool(
    "TRELLO_GET_CARDS_BOARD_BY_ID_CARD",
    description="Get board by card id. Fetches detailed information about the trello board to which a specific, existing, and accessible card belongs, using the card's id or short link.",
)
def TRELLO_GET_CARDS_BOARD_BY_ID_CARD(
    id_card: Annotated[str, "The ID of the card to get board information for."],
    fields: Annotated[str, "The fields to retrieve from the board (e.g., id, name, desc, closed). Defaults to all."] = "all"
):
    """Get board by card id. Fetches detailed information about the trello board to which a specific, existing, and accessible card belongs, using the card's id or short link."""
    err = _validate_required({"id_card": id_card}, ["id_card"])
    if err:
        return err
    
    try:
        # Get board information for the card
        endpoint = f"/cards/{id_card}/board"
        
        # Build query parameters
        params = {}
        if fields is not None:
            params["fields"] = fields
        
        # Make the API request
        result = trello_request("GET", endpoint, params=params)
        
        if not isinstance(result, dict):
            return {
                "successful": False,
                "error": "Invalid board data received",
                "action": "get_card_board",
                "card_id": id_card,
                "message": f"Failed to retrieve board information for card {id_card}"
            }
        
        return {
            "successful": True,
            "data": result,
            "action": "get_card_board",
            "card_id": id_card,
            "message": f"Successfully retrieved board information for card {id_card}",
            "board": result
        }
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve card board: {str(e)}",
            "action": "get_card_board",
            "card_id": id_card,
            "message": f"Failed to retrieve board information for card {id_card}"
        }


@mcp.tool(
    "TRELLO_GET_CARDS_BOARD_BY_ID_CARD_BY_FIELD",
    description="Get board field by card ID. Retrieves a specific field from the board associated with a given trello card.",
)
def TRELLO_GET_CARDS_BOARD_BY_ID_CARD_BY_FIELD(
    field: Annotated[str, "The field to retrieve from the board (e.g., id, name, desc, closed)."],
    id_card: Annotated[str, "The ID of the card to get board field from."]
):
    """Get board field by card ID. Retrieves a specific field from the board associated with a given trello card."""
    err = _validate_required({"field": field, "id_card": id_card}, ["field", "id_card"])
    if err:
        return err
    
    try:
        # Get specific board field for the card
        endpoint = f"/cards/{id_card}/board"
        
        # Build query parameters
        params = {"fields": field}
        
        # Make the API request
        result = trello_request("GET", endpoint, params=params)
        
        if not isinstance(result, dict):
            return {
                "successful": False,
                "error": "Invalid board field data received",
                "action": "get_card_board_field",
                "card_id": id_card,
                "field": field,
                "message": f"Failed to retrieve board field '{field}' for card {id_card}"
            }
        
        return {
            "successful": True,
            "data": result,
            "action": "get_card_board_field",
            "card_id": id_card,
            "field": field,
            "message": f"Successfully retrieved board field '{field}' for card {id_card}",
            "board_field": result
        }
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve card board field: {str(e)}",
            "action": "get_card_board_field",
            "card_id": id_card,
            "field": field,
            "message": f"Failed to retrieve board field '{field}' for card {id_card}"
        }


@mcp.tool(
    "TRELLO_GET_CARDS_BY_ID_CARD_BY_FIELD",
    description="Get card field by id. Retrieves the value of a single, specified field from a trello card.",
)
def TRELLO_GET_CARDS_BY_ID_CARD_BY_FIELD(
    field: Annotated[str, "The field to retrieve from the card (e.g., id, name, desc, closed, due)."],
    id_card: Annotated[str, "The ID of the card to get field from."]
):
    """Get card field by id. Retrieves the value of a single, specified field from a trello card."""
    err = _validate_required({"field": field, "id_card": id_card}, ["field", "id_card"])
    if err:
        return err
    
    try:
        # Get specific field for the card
        endpoint = f"/cards/{id_card}"
        
        # Build query parameters
        params = {"fields": field}
        
        # Make the API request
        result = trello_request("GET", endpoint, params=params)
        
        if not isinstance(result, dict):
            return {
                "successful": False,
                "error": "Invalid card field data received",
                "action": "get_card_field",
                "card_id": id_card,
                "field": field,
                "message": f"Failed to retrieve card field '{field}' for card {id_card}"
            }
        
        return {
            "successful": True,
            "data": result,
            "action": "get_card_field",
            "card_id": id_card,
            "field": field,
            "message": f"Successfully retrieved card field '{field}' for card {id_card}",
            "card_field": result
        }
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve card field: {str(e)}",
            "action": "get_card_field",
            "card_id": id_card,
            "field": field,
            "message": f"Failed to retrieve card field '{field}' for card {id_card}"
        }


@mcp.tool(
    "TRELLO_GET_CARDS_CHECK_ITEM_STATES_BY_ID_CARD",
    description="Get card check item states. Gets the states (e.g., 'complete', 'incomplete') of checklist items on a trello card; returns only item states, not full checklist or card details.",
)
def TRELLO_GET_CARDS_CHECK_ITEM_STATES_BY_ID_CARD(
    id_card: Annotated[str, "The ID of the card to get check item states from."],
    fields: Annotated[str, "The fields to retrieve from the check item states (e.g., idCheckItem, state). Defaults to all."] = "all"
):
    """Get card check item states. Gets the states (e.g., 'complete', 'incomplete') of checklist items on a trello card; returns only item states, not full checklist or card details."""
    err = _validate_required({"id_card": id_card}, ["id_card"])
    if err:
        return err
    
    try:
        # Get check item states for the card
        endpoint = f"/cards/{id_card}/checkItemStates"
        
        # Build query parameters
        params = {}
        if fields is not None:
            params["fields"] = fields
        
        # Make the API request
        result = trello_request("GET", endpoint, params=params)
        
        if not isinstance(result, list):
            return {
                "successful": False,
                "error": "Invalid check item states data received",
                "action": "get_card_check_item_states",
                "card_id": id_card,
                "message": f"Failed to retrieve check item states for card {id_card}"
            }
        
        return {
            "successful": True,
            "data": result,
            "action": "get_card_check_item_states",
            "card_id": id_card,
            "check_item_states_count": len(result),
            "message": f"Successfully retrieved {len(result)} check item states for card {id_card}",
            "check_item_states": result
        }
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve card check item states: {str(e)}",
            "action": "get_card_check_item_states",
            "card_id": id_card,
            "message": f"Failed to retrieve check item states for card {id_card}"
        }


@mcp.tool(
    "TRELLO_GET_CARDS_CHECKLISTS_BY_ID_CARD",
    description="Get card checklists by ID. Retrieves all checklists, including their check items, for a trello card specified by its id or shortlink, if the card exists and is accessible.",
)
def TRELLO_GET_CARDS_CHECKLISTS_BY_ID_CARD(
    id_card: Annotated[str, "The ID of the card to get checklists from."],
    card_fields: Annotated[str, "The fields to retrieve from the card (e.g., id, name, desc). Defaults to all."] = "all",
    cards: Annotated[str, "Whether to include card information. Defaults to none."] = "none",
    check_item_fields: Annotated[str, "The fields to retrieve from check items (e.g., name, nameData, pos, state). Defaults to name,nameData,pos,state."] = "name,nameData,pos,state",
    check_items: Annotated[str, "Whether to include check items. Defaults to all."] = "all",
    fields: Annotated[str, "The fields to retrieve from the checklists (e.g., id, name, pos). Defaults to all."] = "all",
    filter: Annotated[str, "The types of checklists to return. Defaults to all."] = "all"
):
    """Get card checklists by ID. Retrieves all checklists, including their check items, for a trello card specified by its id or shortlink, if the card exists and is accessible."""
    err = _validate_required({"id_card": id_card}, ["id_card"])
    if err:
        return err
    
    try:
        # Get checklists for the card
        endpoint = f"/cards/{id_card}/checklists"
        
        # Build query parameters
        params = {}
        if card_fields is not None:
            params["card_fields"] = card_fields
        if cards is not None:
            params["cards"] = cards
        if check_item_fields is not None:
            params["checkItem_fields"] = check_item_fields
        if check_items is not None:
            params["checkItems"] = check_items
        if fields is not None:
            params["fields"] = fields
        if filter is not None:
            params["filter"] = filter
        
        # Make the API request
        result = trello_request("GET", endpoint, params=params)
        
        if not isinstance(result, list):
            return {
                "successful": False,
                "error": "Invalid checklists data received",
                "action": "get_card_checklists",
                "card_id": id_card,
                "message": f"Failed to retrieve checklists for card {id_card}"
            }
        
        return {
            "successful": True,
            "data": result,
            "action": "get_card_checklists",
            "card_id": id_card,
            "checklists_count": len(result),
            "message": f"Successfully retrieved {len(result)} checklists for card {id_card}",
            "checklists": result
        }
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve card checklists: {str(e)}",
            "action": "get_card_checklists",
            "card_id": id_card,
            "message": f"Failed to retrieve checklists for card {id_card}"
        }


@mcp.tool(
    "TRELLO_GET_CARDS_LIST_BY_ID_CARD",
    description="Get list by card ID. Gets the trello list to which a specified card (which must exist) belongs.",
)
def TRELLO_GET_CARDS_LIST_BY_ID_CARD(
    id_card: Annotated[str, "The ID of the card to get list information for."],
    fields: Annotated[str, "The fields to retrieve from the list (e.g., id, name, closed, pos). Defaults to all."] = "all"
):
    """Get list by card ID. Gets the trello list to which a specified card (which must exist) belongs."""
    err = _validate_required({"id_card": id_card}, ["id_card"])
    if err:
        return err
    
    try:
        # Get list information for the card
        endpoint = f"/cards/{id_card}/list"
        
        # Build query parameters
        params = {}
        if fields is not None:
            params["fields"] = fields
        
        # Make the API request
        result = trello_request("GET", endpoint, params=params)
        
        if not isinstance(result, dict):
            return {
                "successful": False,
                "error": "Invalid list data received",
                "action": "get_card_list",
                "card_id": id_card,
                "message": f"Failed to retrieve list information for card {id_card}"
            }
        
        return {
            "successful": True,
            "data": result,
            "action": "get_card_list",
            "card_id": id_card,
            "message": f"Successfully retrieved list information for card {id_card}",
            "list": result
        }
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve card list: {str(e)}",
            "action": "get_card_list",
            "card_id": id_card,
            "message": f"Failed to retrieve list information for card {id_card}"
        }


@mcp.tool(
    "TRELLO_GET_CARDS_LIST_BY_ID_CARD_BY_FIELD",
    description="Get card list field. Fetches a specific field from the trello list that a given card belongs to.",
)
def TRELLO_GET_CARDS_LIST_BY_ID_CARD_BY_FIELD(
    field: Annotated[str, "The field to retrieve from the list (e.g., id, name, closed, pos)."],
    id_card: Annotated[str, "The ID of the card to get list field from."]
):
    """Get card list field. Fetches a specific field from the trello list that a given card belongs to."""
    err = _validate_required({"field": field, "id_card": id_card}, ["field", "id_card"])
    if err:
        return err
    
    try:
        # Get specific list field for the card
        endpoint = f"/cards/{id_card}/list"
        
        # Build query parameters
        params = {"fields": field}
        
        # Make the API request
        result = trello_request("GET", endpoint, params=params)
        
        if not isinstance(result, dict):
            return {
                "successful": False,
                "error": "Invalid list field data received",
                "action": "get_card_list_field",
                "card_id": id_card,
                "field": field,
                "message": f"Failed to retrieve list field '{field}' for card {id_card}"
            }
        
        return {
            "successful": True,
            "data": result,
            "action": "get_card_list_field",
            "card_id": id_card,
            "field": field,
            "message": f"Successfully retrieved list field '{field}' for card {id_card}",
            "list_field": result
        }
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve card list field: {str(e)}",
            "action": "get_card_list_field",
            "card_id": id_card,
            "field": field,
            "message": f"Failed to retrieve list field '{field}' for card {id_card}"
        }


@mcp.tool(
    "TRELLO_GET_CARDS_MEMBERS_BY_ID_CARD",
    description="Get card members. Retrieves members of a trello card, identified by its id or shortlink, allowing customization of which member fields are returned.",
)
def TRELLO_GET_CARDS_MEMBERS_BY_ID_CARD(
    id_card: Annotated[str, "The ID of the card to get members from."],
    fields: Annotated[str, "The fields to retrieve from the members (e.g., avatarHash, fullName, initials, username). Defaults to avatarHash,fullName,initials,username."] = "avatarHash,fullName,initials,username"
):
    """Get card members. Retrieves members of a trello card, identified by its id or shortlink, allowing customization of which member fields are returned."""
    err = _validate_required({"id_card": id_card}, ["id_card"])
    if err:
        return err
    
    try:
        # Get members for the card
        endpoint = f"/cards/{id_card}/members"
        
        # Build query parameters
        params = {}
        if fields is not None:
            params["fields"] = fields
        
        # Make the API request
        result = trello_request("GET", endpoint, params=params)
        
        if not isinstance(result, list):
            return {
                "successful": False,
                "error": "Invalid members data received",
                "action": "get_card_members",
                "card_id": id_card,
                "message": f"Failed to retrieve members for card {id_card}"
            }
        
        return {
            "successful": True,
            "data": result,
            "action": "get_card_members",
            "card_id": id_card,
            "members_count": len(result),
            "message": f"Successfully retrieved {len(result)} members for card {id_card}",
            "members": result
        }
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve card members: {str(e)}",
            "action": "get_card_members",
            "card_id": id_card,
            "message": f"Failed to retrieve members for card {id_card}"
        }


@mcp.tool(
    "TRELLO_GET_CARDS_MEMBERS_VOTED_BY_ID_CARD",
    description="Get card members voted. Fetches members who voted on a trello card; requires an existing card id, the voting power-up to be active on the board, and members to have voted; returns member details, not vote counts.",
)
def TRELLO_GET_CARDS_MEMBERS_VOTED_BY_ID_CARD(
    id_card: Annotated[str, "The ID of the card to get voted members from."],
    fields: Annotated[str, "The fields to retrieve from the voted members (e.g., avatarHash, fullName, initials, username). Defaults to avatarHash,fullName,initials,username."] = "avatarHash,fullName,initials,username"
):
    """Get card members voted. Fetches members who voted on a trello card; requires an existing card id, the voting power-up to be active on the board, and members to have voted; returns member details, not vote counts."""
    err = _validate_required({"id_card": id_card}, ["id_card"])
    if err:
        return err
    
    try:
        # Get members who voted on the card
        endpoint = f"/cards/{id_card}/membersVoted"
        
        # Build query parameters
        params = {}
        if fields is not None:
            params["fields"] = fields
        
        # Make the API request
        result = trello_request("GET", endpoint, params=params)
        
        if not isinstance(result, list):
            return {
                "successful": False,
                "error": "Invalid voted members data received",
                "action": "get_card_members_voted",
                "card_id": id_card,
                "message": f"Failed to retrieve voted members for card {id_card}"
            }
        
        return {
            "successful": True,
            "data": result,
            "action": "get_card_members_voted",
            "card_id": id_card,
            "voted_members_count": len(result),
            "message": f"Successfully retrieved {len(result)} voted members for card {id_card}",
            "voted_members": result,
            "note": "Requires voting power-up to be active on the board and members to have voted"
        }
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve card voted members: {str(e)}",
            "action": "get_card_members_voted",
            "card_id": id_card,
            "message": f"Failed to retrieve voted members for card {id_card}",
            "note": "This may fail if voting power-up is not active or no members have voted"
        }


@mcp.tool(
    "TRELLO_GET_CARDS_STICKERS_BY_ID_CARD",
    description="Get card stickers by ID card. Retrieves all visual stickers (used for categorization, emphasis, or decoration) from an existing and accessible trello card; this read-only action does not affect other card elements.",
)
def TRELLO_GET_CARDS_STICKERS_BY_ID_CARD(
    id_card: Annotated[str, "The ID of the card to get stickers from."],
    fields: Annotated[str, "The fields to retrieve from the stickers (e.g., id, image, imageUrl, left, top, zIndex). Defaults to all."] = "all"
):
    """Get card stickers by ID card. Retrieves all visual stickers (used for categorization, emphasis, or decoration) from an existing and accessible trello card; this read-only action does not affect other card elements."""
    err = _validate_required({"id_card": id_card}, ["id_card"])
    if err:
        return err
    
    try:
        # Get stickers for the card
        endpoint = f"/cards/{id_card}/stickers"
        
        # Build query parameters
        params = {}
        if fields is not None:
            params["fields"] = fields
        
        # Make the API request
        result = trello_request("GET", endpoint, params=params)
        
        if not isinstance(result, list):
            return {
                "successful": False,
                "error": "Invalid stickers data received",
                "action": "get_card_stickers",
                "card_id": id_card,
                "message": f"Failed to retrieve stickers for card {id_card}"
            }
        
        return {
            "successful": True,
            "data": result,
            "action": "get_card_stickers",
            "card_id": id_card,
            "stickers_count": len(result),
            "message": f"Successfully retrieved {len(result)} stickers for card {id_card}",
            "stickers": result
        }
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve card stickers: {str(e)}",
            "action": "get_card_stickers",
            "card_id": id_card,
            "message": f"Failed to retrieve stickers for card {id_card}"
        }


@mcp.tool(
    "TRELLO_GET_CARDS_STICKERS_BY_ID_CARD_BY_ID_STICKER",
    description="Get card sticker by id. Call this action to retrieve detailed properties (like image, position, rotation) of a specific sticker on a trello card.",
)
def TRELLO_GET_CARDS_STICKERS_BY_ID_CARD_BY_ID_STICKER(
    id_card: Annotated[str, "The ID of the card containing the sticker."],
    id_sticker: Annotated[str, "The ID of the sticker to retrieve."],
    fields: Annotated[str, "The fields to retrieve from the sticker (e.g., id, image, imageUrl, left, top, zIndex, rotation). Defaults to all."] = "all"
):
    """Get card sticker by id. Call this action to retrieve detailed properties (like image, position, rotation) of a specific sticker on a trello card."""
    err = _validate_required({"id_card": id_card, "id_sticker": id_sticker}, ["id_card", "id_sticker"])
    if err:
        return err
    
    try:
        # Get specific sticker from the card
        endpoint = f"/cards/{id_card}/stickers/{id_sticker}"
        
        # Build query parameters
        params = {}
        if fields is not None:
            params["fields"] = fields
        
        # Make the API request
        result = trello_request("GET", endpoint, params=params)
        
        if not isinstance(result, dict):
            return {
                "successful": False,
                "error": "Invalid sticker data received",
                "action": "get_card_sticker",
                "card_id": id_card,
                "sticker_id": id_sticker,
                "message": f"Failed to retrieve sticker {id_sticker} from card {id_card}"
            }
        
        return {
            "successful": True,
            "data": result,
            "action": "get_card_sticker",
            "card_id": id_card,
            "sticker_id": id_sticker,
            "message": f"Successfully retrieved sticker {id_sticker} from card {id_card}",
            "sticker": result
        }
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve card sticker: {str(e)}",
            "action": "get_card_sticker",
            "card_id": id_card,
            "sticker_id": id_sticker,
            "message": f"Failed to retrieve sticker {id_sticker} from card {id_card}"
        }


@mcp.tool(
    "TRELLO_GET_CHECK_ITEM_BY_ID",
    description="Get check item by id. Retrieves a specific check item from a checklist using the checklist id and check item id.",
)
def TRELLO_GET_CHECK_ITEM_BY_ID(
    id_checklist: Annotated[str, "The ID of the checklist containing the check item."],
    id_check_item: Annotated[str, "The ID of the check item to retrieve."],
    fields: Annotated[str, "The fields to retrieve from the check item (e.g., name, nameData, pos, state). Defaults to name,nameData,pos,state."] = "name,nameData,pos,state"
):
    """Get check item by id. Retrieves a specific check item from a checklist using the checklist id and check item id."""
    err = _validate_required({"id_checklist": id_checklist, "id_check_item": id_check_item}, ["id_checklist", "id_check_item"])
    if err:
        return err
    
    try:
        # Get specific check item from the checklist
        endpoint = f"/checklists/{id_checklist}/checkItems/{id_check_item}"
        
        # Build query parameters
        params = {}
        if fields is not None:
            params["fields"] = fields
        
        # Make the API request
        result = trello_request("GET", endpoint, params=params)
        
        if not isinstance(result, dict):
            return {
                "successful": False,
                "error": "Invalid check item data received",
                "action": "get_check_item",
                "checklist_id": id_checklist,
                "check_item_id": id_check_item,
                "message": f"Failed to retrieve check item {id_check_item} from checklist {id_checklist}"
            }
        
        return {
            "successful": True,
            "data": result,
            "action": "get_check_item",
            "checklist_id": id_checklist,
            "check_item_id": id_check_item,
            "message": f"Successfully retrieved check item {id_check_item} from checklist {id_checklist}",
            "check_item": result
        }
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve check item: {str(e)}",
            "action": "get_check_item",
            "checklist_id": id_checklist,
            "check_item_id": id_check_item,
            "message": f"Failed to retrieve check item {id_check_item} from checklist {id_checklist}"
        }


@mcp.tool(
    "TRELLO_GET_CHECKLISTS_BOARD_BY_ID_CHECKLIST",
    description="Get board for a checklist. Retrieves the trello board a specific checklist belongs to, using the checklist id.",
)
def TRELLO_GET_CHECKLISTS_BOARD_BY_ID_CHECKLIST(
    id_checklist: Annotated[str, "The ID of the checklist to get board information for."],
    fields: Annotated[str, "The fields to retrieve from the board (e.g., id, name, desc, closed). Defaults to all."] = "all"
):
    """Get board for a checklist. Retrieves the trello board a specific checklist belongs to, using the checklist id."""
    err = _validate_required({"id_checklist": id_checklist}, ["id_checklist"])
    if err:
        return err
    
    try:
        # Get board information for the checklist
        endpoint = f"/checklists/{id_checklist}/board"
        
        # Build query parameters
        params = {}
        if fields is not None:
            params["fields"] = fields
        
        # Make the API request
        result = trello_request("GET", endpoint, params=params)
        
        if not isinstance(result, dict):
            return {
                "successful": False,
                "error": "Invalid board data received",
                "action": "get_checklist_board",
                "checklist_id": id_checklist,
                "message": f"Failed to retrieve board information for checklist {id_checklist}"
            }
        
        return {
            "successful": True,
            "data": result,
            "action": "get_checklist_board",
            "checklist_id": id_checklist,
            "message": f"Successfully retrieved board information for checklist {id_checklist}",
            "board": result
        }
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve checklist board: {str(e)}",
            "action": "get_checklist_board",
            "checklist_id": id_checklist,
            "message": f"Failed to retrieve board information for checklist {id_checklist}"
        }


@mcp.tool(
    "TRELLO_GET_CHECKLISTS_BOARD_BY_ID_CHECKLIST_BY_FIELD",
    description="Get checklist's board field. Retrieves a specified field (e.g., 'name', 'desc') from the trello board associated with the given idchecklist.",
)
def TRELLO_GET_CHECKLISTS_BOARD_BY_ID_CHECKLIST_BY_FIELD(
    field: Annotated[str, "The field to retrieve from the board (e.g., name, desc, closed, url)."],
    id_checklist: Annotated[str, "The ID of the checklist to get board field from."]
):
    """Get checklist's board field. Retrieves a specified field (e.g., 'name', 'desc') from the trello board associated with the given idchecklist."""
    err = _validate_required({"field": field, "id_checklist": id_checklist}, ["field", "id_checklist"])
    if err:
        return err
    
    try:
        # Get specific board field for the checklist
        endpoint = f"/checklists/{id_checklist}/board"
        
        # Build query parameters
        params = {"fields": field}
        
        # Make the API request
        result = trello_request("GET", endpoint, params=params)
        
        if not isinstance(result, dict):
            return {
                "successful": False,
                "error": "Invalid board field data received",
                "action": "get_checklist_board_field",
                "checklist_id": id_checklist,
                "field": field,
                "message": f"Failed to retrieve board field '{field}' for checklist {id_checklist}"
            }
        
        return {
            "successful": True,
            "data": result,
            "action": "get_checklist_board_field",
            "checklist_id": id_checklist,
            "field": field,
            "message": f"Successfully retrieved board field '{field}' for checklist {id_checklist}",
            "board_field": result
        }
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve checklist board field: {str(e)}",
            "action": "get_checklist_board_field",
            "checklist_id": id_checklist,
            "field": field,
            "message": f"Failed to retrieve board field '{field}' for checklist {id_checklist}"
        }


@mcp.tool(
    "TRELLO_GET_CHECKLISTS_BY_ID_CHECKLIST",
    description="Get checklist by ID. Fetches a trello checklist by its idchecklist, requiring the id to refer to an existing checklist, and allows specifying which details of the checklist, its cards, and check items are returned.",
)
def TRELLO_GET_CHECKLISTS_BY_ID_CHECKLIST(
    id_checklist: Annotated[str, "The ID of the checklist to retrieve."],
    card_fields: Annotated[str, "The fields to retrieve from the cards (e.g., id, name, desc, closed). Defaults to all."] = "all",
    cards: Annotated[str, "Whether to include card information. Defaults to none."] = "none",
    check_item_fields: Annotated[str, "The fields to retrieve from check items (e.g., name, nameData, pos, state). Defaults to name,nameData,pos,state."] = "name,nameData,pos,state",
    check_items: Annotated[str, "Whether to include check items. Defaults to all."] = "all",
    fields: Annotated[str, "The fields to retrieve from the checklist (e.g., id, name, pos). Defaults to all."] = "all"
):
    """Get checklist by ID. Fetches a trello checklist by its idchecklist, requiring the id to refer to an existing checklist, and allows specifying which details of the checklist, its cards, and check items are returned."""
    err = _validate_required({"id_checklist": id_checklist}, ["id_checklist"])
    if err:
        return err
    
    try:
        # Get checklist by ID
        endpoint = f"/checklists/{id_checklist}"
        
        # Build query parameters
        params = {}
        if card_fields is not None:
            params["card_fields"] = card_fields
        if cards is not None:
            params["cards"] = cards
        if check_item_fields is not None:
            params["checkItem_fields"] = check_item_fields
        if check_items is not None:
            params["checkItems"] = check_items
        if fields is not None:
            params["fields"] = fields
        
        # Make the API request
        result = trello_request("GET", endpoint, params=params)
        
        if not isinstance(result, dict):
            return {
                "successful": False,
                "error": "Invalid checklist data received",
                "action": "get_checklist",
                "checklist_id": id_checklist,
                "message": f"Failed to retrieve checklist {id_checklist}"
            }
        
        return {
            "successful": True,
            "data": result,
            "action": "get_checklist",
            "checklist_id": id_checklist,
            "message": f"Successfully retrieved checklist {id_checklist}",
            "checklist": result
        }
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve checklist: {str(e)}",
            "action": "get_checklist",
            "checklist_id": id_checklist,
            "message": f"Failed to retrieve checklist {id_checklist}"
        }


@mcp.tool(
    "TRELLO_GET_CHECKLISTS_BY_ID_CHECKLIST_BY_FIELD",
    description="Get checklist field. Retrieves a specific field's value from a trello checklist by its id and the field name, without loading the entire checklist object or its items.",
)
def TRELLO_GET_CHECKLISTS_BY_ID_CHECKLIST_BY_FIELD(
    field: Annotated[str, "The field to retrieve from the checklist (e.g., id, name, pos, idBoard)."],
    id_checklist: Annotated[str, "The ID of the checklist to get field from."]
):
    """Get checklist field. Retrieves a specific field's value from a trello checklist by its id and the field name, without loading the entire checklist object or its items."""
    err = _validate_required({"field": field, "id_checklist": id_checklist}, ["field", "id_checklist"])
    if err:
        return err
    
    try:
        # Get specific field for the checklist
        endpoint = f"/checklists/{id_checklist}"
        
        # Build query parameters
        params = {"fields": field}
        
        # Make the API request
        result = trello_request("GET", endpoint, params=params)
        
        if not isinstance(result, dict):
            return {
                "successful": False,
                "error": "Invalid checklist field data received",
                "action": "get_checklist_field",
                "checklist_id": id_checklist,
                "field": field,
                "message": f"Failed to retrieve checklist field '{field}' for checklist {id_checklist}"
            }
        
        return {
            "successful": True,
            "data": result,
            "action": "get_checklist_field",
            "checklist_id": id_checklist,
            "field": field,
            "message": f"Successfully retrieved checklist field '{field}' for checklist {id_checklist}",
            "checklist_field": result
        }
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve checklist field: {str(e)}",
            "action": "get_checklist_field",
            "checklist_id": id_checklist,
            "field": field,
            "message": f"Failed to retrieve checklist field '{field}' for checklist {id_checklist}"
        }


@mcp.tool(
    "TRELLO_GET_CHECKLISTS_CARDS_BY_ID_CHECKLIST_BY_FILTER",
    description="Get cards from a checklist by filter. Retrieves cards from a specified trello checklist, filterable by card id or status (e.g., 'all', 'open'), noting the response is a single card object even if the filter could match multiple cards.",
)
def TRELLO_GET_CHECKLISTS_CARDS_BY_ID_CHECKLIST_BY_FILTER(
    filter: Annotated[str, "The filter to apply to cards (e.g., 'all', 'open', 'closed', or specific card ID)."],
    id_checklist: Annotated[str, "The ID of the checklist to get cards from."]
):
    """Get cards from a checklist by filter. Retrieves cards from a specified trello checklist, filterable by card id or status (e.g., 'all', 'open'), noting the response is a single card object even if the filter could match multiple cards."""
    err = _validate_required({"filter": filter, "id_checklist": id_checklist}, ["filter", "id_checklist"])
    if err:
        return err
    
    try:
        # Get cards from the checklist with filter
        endpoint = f"/checklists/{id_checklist}/cards"
        
        # Build query parameters
        params = {"filter": filter}
        
        # Make the API request
        result = trello_request("GET", endpoint, params=params)
        
        if not isinstance(result, list):
            return {
                "successful": False,
                "error": "Invalid cards data received",
                "action": "get_checklist_cards_filtered",
                "checklist_id": id_checklist,
                "filter": filter,
                "message": f"Failed to retrieve cards from checklist {id_checklist} with filter '{filter}'"
            }
        
        # Get the first card if multiple cards match the filter
        first_card = result[0] if result else None
        
        return {
            "successful": True,
            "data": first_card,
            "action": "get_checklist_cards_filtered",
            "checklist_id": id_checklist,
            "filter": filter,
            "cards_count": len(result),
            "message": f"Successfully retrieved cards from checklist {id_checklist} with filter '{filter}'",
            "card": first_card,
            "all_cards": result,
            "note": "Returns the first card from the filtered results. Use 'all_cards' to access all matching cards."
        }
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve checklist cards: {str(e)}",
            "action": "get_checklist_cards_filtered",
            "checklist_id": id_checklist,
            "filter": filter,
            "message": f"Failed to retrieve cards from checklist {id_checklist} with filter '{filter}'"
        }


@mcp.tool(
    "TRELLO_GET_CHECKLISTS_CHECK_ITEMS_BY_ID_CHECKLIST",
    description="Get checklist items by ID. Retrieves check items from an existing trello checklist, optionally filtering them and specifying which fields to return.",
)
def TRELLO_GET_CHECKLISTS_CHECK_ITEMS_BY_ID_CHECKLIST(
    id_checklist: Annotated[str, "The ID of the checklist to get check items from."],
    fields: Annotated[str, "The fields to retrieve from the check items (e.g., name, nameData, pos, state). Defaults to name,nameData,pos,state."] = "name,nameData,pos,state",
    filter: Annotated[str, "The filter to apply to check items (e.g., 'all', 'visible'). Defaults to all."] = "all"
):
    """Get checklist items by ID. Retrieves check items from an existing trello checklist, optionally filtering them and specifying which fields to return."""
    err = _validate_required({"id_checklist": id_checklist}, ["id_checklist"])
    if err:
        return err
    
    try:
        # Get check items from the checklist
        endpoint = f"/checklists/{id_checklist}/checkItems"
        
        # Build query parameters
        params = {}
        if fields is not None:
            params["fields"] = fields
        if filter is not None:
            params["filter"] = filter
        
        # Make the API request
        result = trello_request("GET", endpoint, params=params)
        
        if not isinstance(result, list):
            return {
                "successful": False,
                "error": "Invalid check items data received",
                "action": "get_checklist_check_items",
                "checklist_id": id_checklist,
                "message": f"Failed to retrieve check items from checklist {id_checklist}"
            }
        
        return {
            "successful": True,
            "data": result,
            "action": "get_checklist_check_items",
            "checklist_id": id_checklist,
            "check_items_count": len(result),
            "message": f"Successfully retrieved {len(result)} check items from checklist {id_checklist}",
            "check_items": result
        }
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve checklist check items: {str(e)}",
            "action": "get_checklist_check_items",
            "checklist_id": id_checklist,
            "message": f"Failed to retrieve check items from checklist {id_checklist}"
        }


@mcp.tool(
    "TRELLO_GET_LABELS_BOARD_BY_ID_LABEL",
    description="Get board by label ID. Retrieves the trello board to which a given, valid trello label id (idlabel) belongs.",
)
def TRELLO_GET_LABELS_BOARD_BY_ID_LABEL(
    id_label: Annotated[str, "The ID of the label to get board information for."],
    fields: Annotated[str, "The fields to retrieve from the board (e.g., id, name, desc, closed). Defaults to all."] = "all"
):
    """Get board by label ID. Retrieves the trello board to which a given, valid trello label id (idlabel) belongs."""
    err = _validate_required({"id_label": id_label}, ["id_label"])
    if err:
        return err
    
    try:
        # Get board information for the label
        endpoint = f"/labels/{id_label}/board"
        
        # Build query parameters
        params = {}
        if fields is not None:
            params["fields"] = fields
        
        # Make the API request
        result = trello_request("GET", endpoint, params=params)
        
        if not isinstance(result, dict):
            return {
                "successful": False,
                "error": "Invalid board data received",
                "action": "get_label_board",
                "label_id": id_label,
                "message": f"Failed to retrieve board information for label {id_label}"
            }
        
        return {
            "successful": True,
            "data": result,
            "action": "get_label_board",
            "label_id": id_label,
            "message": f"Successfully retrieved board information for label {id_label}",
            "board": result
        }
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve label board: {str(e)}",
            "action": "get_label_board",
            "label_id": id_label,
            "message": f"Failed to retrieve board information for label {id_label}"
        }


@mcp.tool(
    "TRELLO_GET_LABELS_BOARD_BY_ID_LABEL_BY_FIELD",
    description="Retrieve board field by label id. Retrieves a specified field (e.g., 'name', 'url') from the trello board associated with a given idlabel.",
)
def TRELLO_GET_LABELS_BOARD_BY_ID_LABEL_BY_FIELD(
    field: Annotated[str, "The field to retrieve from the board (e.g., name, url, desc, closed)."],
    id_label: Annotated[str, "The ID of the label to get board field from."]
):
    """Retrieve board field by label id. Retrieves a specified field (e.g., 'name', 'url') from the trello board associated with a given idlabel."""
    err = _validate_required({"field": field, "id_label": id_label}, ["field", "id_label"])
    if err:
        return err
    
    try:
        # Get specific board field for the label
        endpoint = f"/labels/{id_label}/board"
        
        # Build query parameters
        params = {"fields": field}
        
        # Make the API request
        result = trello_request("GET", endpoint, params=params)
        
        if not isinstance(result, dict):
            return {
                "successful": False,
                "error": "Invalid board field data received",
                "action": "get_label_board_field",
                "label_id": id_label,
                "field": field,
                "message": f"Failed to retrieve board field '{field}' for label {id_label}"
            }
        
        return {
            "successful": True,
            "data": result,
            "action": "get_label_board_field",
            "label_id": id_label,
            "field": field,
            "message": f"Successfully retrieved board field '{field}' for label {id_label}",
            "board_field": result
        }
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve label board field: {str(e)}",
            "action": "get_label_board_field",
            "label_id": id_label,
            "field": field,
            "message": f"Failed to retrieve board field '{field}' for label {id_label}"
        }


@mcp.tool(
    "TRELLO_GET_LABELS_BY_ID_LABEL",
    description="Get label by id. Retrieves detailed information for a specific trello label by its id, allowing selection of specific fields to return.",
)
def TRELLO_GET_LABELS_BY_ID_LABEL(
    id_label: Annotated[str, "The ID of the label to retrieve."],
    fields: Annotated[str, "The fields to retrieve from the label (e.g., id, name, color, idBoard). Defaults to all."] = "all"
):
    """Get label by id. Retrieves detailed information for a specific trello label by its id, allowing selection of specific fields to return."""
    err = _validate_required({"id_label": id_label}, ["id_label"])
    if err:
        return err
    
    try:
        # Get label by ID
        endpoint = f"/labels/{id_label}"
        
        # Build query parameters
        params = {}
        if fields is not None:
            params["fields"] = fields
        
        # Make the API request
        result = trello_request("GET", endpoint, params=params)
        
        if not isinstance(result, dict):
            return {
                "successful": False,
                "error": "Invalid label data received",
                "action": "get_label",
                "label_id": id_label,
                "message": f"Failed to retrieve label {id_label}"
            }
        
        return {
            "successful": True,
            "data": result,
            "action": "get_label",
            "label_id": id_label,
            "message": f"Successfully retrieved label {id_label}",
            "label": result
        }
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve label: {str(e)}",
            "action": "get_label",
            "label_id": id_label,
            "message": f"Failed to retrieve label {id_label}"
        }


@mcp.tool(
    "TRELLO_GET_LISTS_ACTIONS_BY_ID_LIST",
    description="Get list actions by ID. Retrieves actions (like card movements or comments, newest first) for a trello list by its id, to track history or create activity logs.",
)
def TRELLO_GET_LISTS_ACTIONS_BY_ID_LIST(
    id_list: Annotated[str, "The ID of the list to get actions for."],
    before: Annotated[str | None, "An action ID. Only return actions before this action."] = None,
    entities: Annotated[str | None, "Whether to include entities in the response."] = None,
    fields: Annotated[str, "The fields to retrieve from the actions (e.g., id, type, date, data). Defaults to all."] = "all",
    filter: Annotated[str, "The types of actions to return (e.g., commentCard, updateCard). Defaults to all."] = "all",
    format: Annotated[str, "The format for the returned actions. Defaults to list."] = "list",
    id_models: Annotated[str | None, "The IDs of models to include in the response."] = None,
    limit: Annotated[str, "The maximum number of actions to return. Defaults to 5."] = "5",
    member: Annotated[str | None, "Whether to include member information."] = None,
    member_creator: Annotated[str | None, "Whether to include member creator information."] = None,
    member_creator_fields: Annotated[str, "The fields to retrieve from member creators. Defaults to avatarHash, fullName, initials and username."] = "avatarHash,fullName,initials,username",
    member_fields: Annotated[str, "The fields to retrieve from members. Defaults to avatarHash, fullName, initials and username."] = "avatarHash,fullName,initials,username",
    page: Annotated[str, "The page of results to return. Defaults to 1."] = "1",
    since: Annotated[str | None, "An action ID. Only return actions after this action."] = None
):
    """Get list actions by ID. Retrieves actions (like card movements or comments, newest first) for a trello list by its id, to track history or create activity logs."""
    err = _validate_required({"id_list": id_list}, ["id_list"])
    if err:
        return err
    
    try:
        # Get actions for the list
        endpoint = f"/lists/{id_list}/actions"
        
        # Build query parameters
        params = {}
        if before is not None:
            params["before"] = before
        if entities is not None:
            params["entities"] = entities
        if fields is not None:
            params["fields"] = fields
        if filter is not None:
            params["filter"] = filter
        if format is not None:
            params["format"] = format
        if id_models is not None:
            params["idModels"] = id_models
        if limit is not None:
            params["limit"] = limit
        if member is not None:
            params["member"] = member
        if member_creator is not None:
            params["memberCreator"] = member_creator
        if member_creator_fields is not None:
            params["memberCreator_fields"] = member_creator_fields
        if member_fields is not None:
            params["member_fields"] = member_fields
        if page is not None:
            params["page"] = page
        if since is not None:
            params["since"] = since
        
        # Make the API request
        result = trello_request("GET", endpoint, params=params)
        
        if not isinstance(result, list):
            return {
                "successful": False,
                "error": "Invalid actions data received",
                "action": "get_list_actions",
                "list_id": id_list,
                "message": f"Failed to retrieve actions for list {id_list}"
            }
        
        return {
            "successful": True,
            "data": result,
            "action": "get_list_actions",
            "list_id": id_list,
            "actions_count": len(result),
            "message": f"Successfully retrieved {len(result)} actions for list {id_list}",
            "actions": result,
            "note": "Actions are returned newest first for activity tracking"
        }
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve list actions: {str(e)}",
            "action": "get_list_actions",
            "list_id": id_list,
            "message": f"Failed to retrieve actions for list {id_list}"
        }

@mcp.tool(
    "TRELLO_GET_LISTS_BOARD_BY_ID_LIST",
    description="Get board by list ID. Retrieves the board to which a specific trello list belongs.",
)
def TRELLO_GET_LISTS_BOARD_BY_ID_LIST(
    id_list: Annotated[str, "The ID of the list to get the board for."],
    fields: Annotated[str, "The fields to retrieve from the board (e.g., id, name, desc, closed). Defaults to all."] = "all"
):
    """Get board by list ID. Retrieves the board to which a specific trello list belongs."""
    err = _validate_required({"id_list": id_list}, ["id_list"])
    if err:
        return err
    
    try:
        # Get board for the list
        endpoint = f"/lists/{id_list}/board"
        
        # Build query parameters
        params = {}
        if fields is not None:
            params["fields"] = fields
        
        # Make the API request
        result = trello_request("GET", endpoint, params=params)
        
        if not isinstance(result, dict):
            return {
                "successful": False,
                "error": "Invalid board data received",
                "action": "get_list_board",
                "list_id": id_list,
                "message": f"Failed to retrieve board for list {id_list}"
            }
        
        return {
            "successful": True,
            "data": result,
            "action": "get_list_board",
            "list_id": id_list,
            "board_id": result.get("id"),
            "board_name": result.get("name"),
            "message": f"Successfully retrieved board for list {id_list}",
            "board": result
        }
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve list board: {str(e)}",
            "action": "get_list_board",
            "list_id": id_list,
            "message": f"Failed to retrieve board for list {id_list}"
        }


@mcp.tool(
    "TRELLO_LIST_ID_BOARD_GET",
    description="Get board by list ID. Deprecated: please use the `get lists board by id list` action instead. retrieves the board to which a specific trello list belongs.",
)
def TRELLO_LIST_ID_BOARD_GET(
    id_list: Annotated[str, "The ID of the list to get the board for."],
    fields: Annotated[str, "The fields to retrieve from the board (e.g., id, name, desc, closed). Defaults to all."] = "all"
):
    """Get board by list ID. Deprecated: please use the `get lists board by id list` action instead. retrieves the board to which a specific trello list belongs."""
    # This is a deprecated wrapper around TRELLO_GET_LISTS_BOARD_BY_ID_LIST
    return TRELLO_GET_LISTS_BOARD_BY_ID_LIST(
        id_list=id_list,
        fields=fields
    )

@mcp.tool(
    "TRELLO_GET_LISTS_BOARD_BY_ID_LIST_BY_FIELD",
    description="Get board field by list ID. Retrieves a specific field (e.g., 'name', 'desc', 'url') from the trello board associated with a given list id, useful when the board's id is not directly known.",
)
def TRELLO_GET_LISTS_BOARD_BY_ID_LIST_BY_FIELD(
    id_list: Annotated[str, "The ID of the list to get the board field for."],
    field: Annotated[str, "The specific field to retrieve from the board (e.g., name, desc, url, closed, idOrganization)."]
):
    """Get board field by list ID. Retrieves a specific field (e.g., 'name', 'desc', 'url') from the trello board associated with a given list id, useful when the board's id is not directly known."""
    err = _validate_required({"id_list": id_list, "field": field}, ["id_list", "field"])
    if err:
        return err
    
    try:
        # Get specific field from board for the list
        endpoint = f"/lists/{id_list}/board"
        
        # Build query parameters
        params = {
            "fields": field
        }
        
        # Make the API request
        result = trello_request("GET", endpoint, params=params)
        
        if not isinstance(result, dict):
            return {
                "successful": False,
                "error": "Invalid board data received",
                "action": "get_list_board_field",
                "list_id": id_list,
                "field": field,
                "message": f"Failed to retrieve board field '{field}' for list {id_list}"
            }
        
        # Extract the specific field value
        field_value = result.get(field)
        
        return {
            "successful": True,
            "data": {field: field_value},
            "action": "get_list_board_field",
            "list_id": id_list,
            "field": field,
            "field_value": field_value,
            "message": f"Successfully retrieved board field '{field}' for list {id_list}",
            "board_field": field_value
        }
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve list board field: {str(e)}",
            "action": "get_list_board_field",
            "list_id": id_list,
            "field": field,
            "message": f"Failed to retrieve board field '{field}' for list {id_list}"
        }

@mcp.tool(
    "TRELLO_GET_LISTS_BY_ID_LIST",
    description="Get list by ID. Retrieves a trello list by its unique id, optionally including details for its cards and parent board.",
)
def TRELLO_GET_LISTS_BY_ID_LIST(
    id_list: Annotated[str, "The ID of the list to retrieve."],
    board: Annotated[str | None, "Whether to include board information."] = None,
    board_fields: Annotated[str, "The fields to retrieve from the board. Defaults to name, desc, descData, closed, idOrganization, pinned, url and prefs."] = "name,desc,descData,closed,idOrganization,pinned,url,prefs",
    card_fields: Annotated[str, "The fields to retrieve from cards. Defaults to all."] = "all",
    cards: Annotated[str, "Whether to include cards in the response. Defaults to none."] = "none",
    fields: Annotated[str, "The fields to retrieve from the list. Defaults to name, closed, idBoard and pos."] = "name,closed,idBoard,pos"
):
    """Get list by ID. Retrieves a trello list by its unique id, optionally including details for its cards and parent board."""
    err = _validate_required({"id_list": id_list}, ["id_list"])
    if err:
        return err
    
    try:
        # Get list by ID
        endpoint = f"/lists/{id_list}"
        
        # Build query parameters
        params = {}
        if board is not None:
            params["board"] = board
        if board_fields is not None:
            params["board_fields"] = board_fields
        if card_fields is not None:
            params["card_fields"] = card_fields
        if cards is not None:
            params["cards"] = cards
        if fields is not None:
            params["fields"] = fields
        
        # Make the API request
        result = trello_request("GET", endpoint, params=params)
        
        if not isinstance(result, dict):
            return {
                "successful": False,
                "error": "Invalid list data received",
                "action": "get_list",
                "list_id": id_list,
                "message": f"Failed to retrieve list {id_list}"
            }
        
        # Extract key information
        list_name = result.get("name")
        list_closed = result.get("closed")
        board_id = result.get("idBoard")
        cards_data = result.get("cards", [])
        board_data = result.get("board")
        
        response = {
            "successful": True,
            "data": result,
            "action": "get_list",
            "list_id": id_list,
            "list_name": list_name,
            "list_closed": list_closed,
            "board_id": board_id,
            "message": f"Successfully retrieved list {id_list}",
            "list": result
        }
        
        # Add cards information if included
        if cards_data:
            response["cards_count"] = len(cards_data)
            response["cards"] = cards_data
        
        # Add board information if included
        if board_data:
            response["board"] = board_data
            response["board_name"] = board_data.get("name")
        
        return response
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve list: {str(e)}",
            "action": "get_list",
            "list_id": id_list,
            "message": f"Failed to retrieve list {id_list}"
        }


@mcp.tool(
    "TRELLO_LIST_GET_BY_ID_LIST",
    description="Get list by ID. Retrieves a trello list by its unique id, optionally including details for its cards and parent board. <<DEPRECATED use get_lists_by_id_list>>",
)
def TRELLO_LIST_GET_BY_ID_LIST(
    id_list: Annotated[str, "The ID of the list to retrieve."],
    board: Annotated[str | None, "Whether to include board information."] = None,
    board_fields: Annotated[str, "The fields to retrieve from the board. Defaults to name, desc, descData, closed, idOrganization, pinned, url and prefs."] = "name,desc,descData,closed,idOrganization,pinned,url,prefs",
    card_fields: Annotated[str, "The fields to retrieve from cards. Defaults to all."] = "all",
    cards: Annotated[str, "Whether to include cards in the response. Defaults to none."] = "none",
    fields: Annotated[str, "The fields to retrieve from the list. Defaults to name, closed, idBoard and pos."] = "name,closed,idBoard,pos"
):
    """Get list by ID. Retrieves a trello list by its unique id, optionally including details for its cards and parent board. <<DEPRECATED use get_lists_by_id_list>>"""
    # This is a deprecated wrapper around TRELLO_GET_LISTS_BY_ID_LIST
    return TRELLO_GET_LISTS_BY_ID_LIST(
        id_list=id_list,
        board=board,
        board_fields=board_fields,
        card_fields=card_fields,
        cards=cards,
        fields=fields
    )

@mcp.tool(
    "TRELLO_GET_LISTS_BY_ID_LIST_BY_FIELD",
    description="Get list field value. Fetches the value of a single, specified field from a trello list.",
)
def TRELLO_GET_LISTS_BY_ID_LIST_BY_FIELD(
    id_list: Annotated[str, "The ID of the list to get the field from."],
    field: Annotated[str, "The specific field to retrieve from the list (e.g., name, closed, idBoard, pos)."]
):
    """Get list field value. Fetches the value of a single, specified field from a trello list."""
    err = _validate_required({"id_list": id_list, "field": field}, ["id_list", "field"])
    if err:
        return err
    
    try:
        # Get specific field from list
        endpoint = f"/lists/{id_list}"
        
        # Build query parameters
        params = {
            "fields": field
        }
        
        # Make the API request
        result = trello_request("GET", endpoint, params=params)
        
        if not isinstance(result, dict):
            return {
                "successful": False,
                "error": "Invalid list data received",
                "action": "get_list_field",
                "list_id": id_list,
                "field": field,
                "message": f"Failed to retrieve list field '{field}' for list {id_list}"
            }
        
        # Extract the specific field value
        field_value = result.get(field)
        
        return {
            "successful": True,
            "data": {field: field_value},
            "action": "get_list_field",
            "list_id": id_list,
            "field": field,
            "field_value": field_value,
            "message": f"Successfully retrieved list field '{field}' for list {id_list}",
            "list_field": field_value
        }
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve list field: {str(e)}",
            "action": "get_list_field",
            "list_id": id_list,
            "field": field,
            "message": f"Failed to retrieve list field '{field}' for list {id_list}"
        }

@mcp.tool(
    "TRELLO_GET_LISTS_CARDS_BY_ID_LIST_BY_FILTER",
    description="Get list cards by filter. Retrieves cards from a specific trello list, filtered by criteria like 'open', 'closed', or 'all'.",
)
def TRELLO_GET_LISTS_CARDS_BY_ID_LIST_BY_FILTER(
    id_list: Annotated[str, "The ID of the list to get cards from."],
    filter: Annotated[str, "The filter criteria for cards (e.g., 'open', 'closed', 'all')."]
):
    """Get list cards by filter. Retrieves cards from a specific trello list, filtered by criteria like 'open', 'closed', or 'all'."""
    err = _validate_required({"id_list": id_list, "filter": filter}, ["id_list", "filter"])
    if err:
        return err
    
    try:
        # Get cards from the list with filter
        endpoint = f"/lists/{id_list}/cards"
        
        # Build query parameters
        params = {
            "filter": filter
        }
        
        # Make the API request
        result = trello_request("GET", endpoint, params=params)
        
        if not isinstance(result, list):
            return {
                "successful": False,
                "error": "Invalid cards data received",
                "action": "get_list_cards_filtered",
                "list_id": id_list,
                "filter": filter,
                "message": f"Failed to retrieve cards with filter '{filter}' for list {id_list}"
            }
        
        # Extract key information
        cards_count = len(result)
        open_cards = [card for card in result if not card.get("closed", False)]
        closed_cards = [card for card in result if card.get("closed", False)]
        
        response = {
            "successful": True,
            "data": result,
            "action": "get_list_cards_filtered",
            "list_id": id_list,
            "filter": filter,
            "cards_count": cards_count,
            "open_cards_count": len(open_cards),
            "closed_cards_count": len(closed_cards),
            "message": f"Successfully retrieved {cards_count} cards with filter '{filter}' for list {id_list}",
            "cards": result
        }
        
        # Add filter-specific information
        if filter == "open":
            response["note"] = "Showing only open (non-closed) cards"
        elif filter == "closed":
            response["note"] = "Showing only closed cards"
        elif filter == "all":
            response["note"] = "Showing all cards (open and closed)"
        else:
            response["note"] = f"Cards filtered by criteria: {filter}"
        
        return response
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve list cards: {str(e)}",
            "action": "get_list_cards_filtered",
            "list_id": id_list,
            "filter": filter,
            "message": f"Failed to retrieve cards with filter '{filter}' for list {id_list}"
        }

@mcp.tool(
    "TRELLO_GET_MEMBER_BOARD_BACKGROUND",
    description="Get Member Board Background. Retrieves a specific custom board background for a trello member, using the member's id and the custom board background's id.",
)
def TRELLO_GET_MEMBER_BOARD_BACKGROUND(
    id_member: Annotated[str, "The ID of the member to get the custom board background for."],
    id_board_background: Annotated[str, "The ID of the custom board background to retrieve."],
    fields: Annotated[str, "The fields to retrieve from the custom board background (e.g., id, name, brightness, tile). Defaults to all."] = "all"
):
    """Get Member Board Background. Retrieves a specific custom board background for a trello member, using the member's id and the custom board background's id."""
    err = _validate_required({"id_member": id_member, "id_board_background": id_board_background}, ["id_member", "id_board_background"])
    if err:
        return err
    
    try:
        # Get member custom board background
        endpoint = f"/members/{id_member}/customBoardBackgrounds/{id_board_background}"
        
        # Build query parameters
        params = {}
        if fields is not None:
            params["fields"] = fields
        
        # Make the API request
        result = trello_request("GET", endpoint, params=params)
        
        if not isinstance(result, dict):
            return {
                "successful": False,
                "error": "Invalid board background data received",
                "action": "get_member_board_background",
                "member_id": id_member,
                "board_background_id": id_board_background,
                "message": f"Failed to retrieve board background {id_board_background} for member {id_member}"
            }
        
        return {
            "successful": True,
            "data": result,
            "action": "get_member_board_background",
            "member_id": id_member,
            "board_background_id": id_board_background,
            "background_name": result.get("name"),
            "background_brightness": result.get("brightness"),
            "background_tile": result.get("tile"),
            "message": f"Successfully retrieved board background {id_board_background} for member {id_member}",
            "board_background": result
        }
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve member board background: {str(e)}",
            "action": "get_member_board_background",
            "member_id": id_member,
            "board_background_id": id_board_background,
            "message": f"Failed to retrieve board background {id_board_background} for member {id_member}"
        }

@mcp.tool(
    "TRELLO_GET_MEMBERS_CUSTOM_BOARD_BACKGROUNDS_BY_ID_MEMBER",
    description="Get Member Custom Board Backgrounds. Retrieves all custom board backgrounds for a trello member.",
)
def TRELLO_GET_MEMBERS_CUSTOM_BOARD_BACKGROUNDS_BY_ID_MEMBER(
    id_member: Annotated[str, "The ID of the member to get custom board backgrounds for."],
    fields: Annotated[str, "The fields to retrieve from the custom board backgrounds (e.g., id, name, brightness, tile). Defaults to all."] = "all"
):
    """Get Member Custom Board Backgrounds. Retrieves all custom board backgrounds for a trello member."""
    err = _validate_required({"id_member": id_member}, ["id_member"])
    if err:
        return err
    
    try:
        # Get all custom board backgrounds for the member
        endpoint = f"/members/{id_member}/customBoardBackgrounds"
        
        # Build query parameters
        params = {}
        if fields is not None:
            params["fields"] = fields
        
        # Make the API request
        result = trello_request("GET", endpoint, params=params)
        
        if not isinstance(result, list):
            return {
                "successful": False,
                "error": "Invalid custom board backgrounds data received",
                "action": "get_member_custom_board_backgrounds",
                "member_id": id_member,
                "message": f"Failed to retrieve custom board backgrounds for member {id_member}"
            }
        
        # Extract key information
        backgrounds_count = len(result)
        background_ids = [bg.get("id") for bg in result if bg.get("id")]
        background_names = [bg.get("name") for bg in result if bg.get("name")]
        
        response = {
            "successful": True,
            "data": result,
            "action": "get_member_custom_board_backgrounds",
            "member_id": id_member,
            "backgrounds_count": backgrounds_count,
            "background_ids": background_ids,
            "background_names": background_names,
            "message": f"Successfully retrieved {backgrounds_count} custom board backgrounds for member {id_member}",
            "custom_board_backgrounds": result
        }
        
        # Add helpful information for using the backgrounds
        if background_ids:
            response["note"] = f"Use any of these background IDs with TRELLO_GET_MEMBER_BOARD_BACKGROUND: {', '.join(background_ids[:5])}{'...' if len(background_ids) > 5 else ''}"
        else:
            response["note"] = "No custom board backgrounds found for this member"
        
        return response
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve member custom board backgrounds: {str(e)}",
            "action": "get_member_custom_board_backgrounds",
            "member_id": id_member,
            "message": f"Failed to retrieve custom board backgrounds for member {id_member}"
        }

@mcp.tool(
    "TRELLO_GET_MEMBER_CUSTOM_BG",
    description="Get member custom board background. Retrieves metadata (e.g., brightness, urls, tiling status) for a specific custom board background of a trello member, not the image file itself.",
)
def TRELLO_GET_MEMBER_CUSTOM_BG(
    id_member: Annotated[str, "The ID of the member to get the custom board background for."],
    id_board_background: Annotated[str, "The ID of the custom board background to retrieve metadata for."],
    fields: Annotated[str, "The fields to retrieve from the custom board background (e.g., id, name, brightness, tile, url). Defaults to all."] = "all"
):
    """Get member custom board background. Retrieves metadata (e.g., brightness, urls, tiling status) for a specific custom board background of a trello member, not the image file itself."""
    err = _validate_required({"id_member": id_member, "id_board_background": id_board_background}, ["id_member", "id_board_background"])
    if err:
        return err
    
    try:
        # Get member custom board background metadata
        endpoint = f"/members/{id_member}/customBoardBackgrounds/{id_board_background}"
        
        # Build query parameters
        params = {}
        if fields is not None:
            params["fields"] = fields
        
        # Make the API request
        result = trello_request("GET", endpoint, params=params)
        
        if not isinstance(result, dict):
            return {
                "successful": False,
                "error": "Invalid custom board background data received",
                "action": "get_member_custom_bg",
                "member_id": id_member,
                "board_background_id": id_board_background,
                "message": f"Failed to retrieve custom board background metadata for member {id_member}"
            }
        
        return {
            "successful": True,
            "data": result,
            "action": "get_member_custom_bg",
            "member_id": id_member,
            "board_background_id": id_board_background,
            "background_name": result.get("name"),
            "background_brightness": result.get("brightness"),
            "background_tile": result.get("tile"),
            "background_url": result.get("url"),
            "background_size": result.get("size"),
            "background_color": result.get("color"),
            "message": f"Successfully retrieved custom board background metadata for member {id_member}",
            "custom_board_background": result
        }
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve member custom board background: {str(e)}",
            "action": "get_member_custom_bg",
            "member_id": id_member,
            "board_background_id": id_board_background,
            "message": f"Failed to retrieve custom board background metadata for member {id_member}"
        }

@mcp.tool(
    "TRELLO_GET_MEMBER_CUSTOM_EMOJI",
    description="Get member custom emoji. Retrieves a specific custom emoji by its id for a trello member, requiring that both the member and emoji exist and are associated.",
)
def TRELLO_GET_MEMBER_CUSTOM_EMOJI(
    id_member: Annotated[str, "The ID of the member to get the custom emoji for."],
    id_custom_emoji: Annotated[str, "The ID of the custom emoji to retrieve."],
    fields: Annotated[str, "The fields to retrieve from the custom emoji (e.g., id, name, url, unscaled). Defaults to all."] = "all"
):
    """Get member custom emoji. Retrieves a specific custom emoji by its id for a trello member, requiring that both the member and emoji exist and are associated."""
    err = _validate_required({"id_member": id_member, "id_custom_emoji": id_custom_emoji}, ["id_member", "id_custom_emoji"])
    if err:
        return err
    
    try:
        # Get member custom emoji
        endpoint = f"/members/{id_member}/customEmoji/{id_custom_emoji}"
        
        # Build query parameters
        params = {}
        if fields is not None:
            params["fields"] = fields
        
        # Make the API request
        result = trello_request("GET", endpoint, params=params)
        
        if not isinstance(result, dict):
            return {
                "successful": False,
                "error": "Invalid custom emoji data received",
                "action": "get_member_custom_emoji",
                "member_id": id_member,
                "custom_emoji_id": id_custom_emoji,
                "message": f"Failed to retrieve custom emoji {id_custom_emoji} for member {id_member}"
            }
        
        return {
            "successful": True,
            "data": result,
            "action": "get_member_custom_emoji",
            "member_id": id_member,
            "custom_emoji_id": id_custom_emoji,
            "emoji_name": result.get("name"),
            "emoji_url": result.get("url"),
            "emoji_unscaled": result.get("unscaled"),
            "message": f"Successfully retrieved custom emoji {id_custom_emoji} for member {id_member}",
            "custom_emoji": result
        }
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve member custom emoji: {str(e)}",
            "action": "get_member_custom_emoji",
            "member_id": id_member,
            "custom_emoji_id": id_custom_emoji,
            "message": f"Failed to retrieve custom emoji {id_custom_emoji} for member {id_member}"
        }

@mcp.tool(
    "TRELLO_GET_MEMBERS_CUSTOM_EMOJI_BY_ID_MEMBER",
    description="Get member custom emoji. Retrieves all custom (user-specific, non-standard) emojis that a specified trello member has created or can access.",
)
def TRELLO_GET_MEMBERS_CUSTOM_EMOJI_BY_ID_MEMBER(
    id_member: Annotated[str, "The ID of the member to get custom emojis for."],
    filter: Annotated[str, "The filter criteria for custom emojis (e.g., 'all', 'mine'). Defaults to all."] = "all"
):
    """Get member custom emoji. Retrieves all custom (user-specific, non-standard) emojis that a specified trello member has created or can access."""
    err = _validate_required({"id_member": id_member}, ["id_member"])
    if err:
        return err
    
    try:
        # Get all custom emojis for the member
        endpoint = f"/members/{id_member}/customEmoji"
        
        # Build query parameters
        params = {}
        if filter is not None:
            params["filter"] = filter
        
        # Make the API request
        result = trello_request("GET", endpoint, params=params)
        
        if not isinstance(result, list):
            return {
                "successful": False,
                "error": "Invalid custom emojis data received",
                "action": "get_members_custom_emoji",
                "member_id": id_member,
                "message": f"Failed to retrieve custom emojis for member {id_member}"
            }
        
        # Extract key information
        emojis_count = len(result)
        emoji_ids = [emoji.get("id") for emoji in result if emoji.get("id")]
        emoji_names = [emoji.get("name") for emoji in result if emoji.get("name")]
        
        response = {
            "successful": True,
            "data": result,
            "action": "get_members_custom_emoji",
            "member_id": id_member,
            "emojis_count": emojis_count,
            "emoji_ids": emoji_ids,
            "emoji_names": emoji_names,
            "message": f"Successfully retrieved {emojis_count} custom emojis for member {id_member}",
            "custom_emojis": result
        }
        
        # Add helpful information for using the emojis
        if emoji_ids:
            response["note"] = f"Use any of these emoji IDs with TRELLO_GET_MEMBER_CUSTOM_EMOJI: {', '.join(emoji_ids[:5])}{'...' if len(emoji_ids) > 5 else ''}"
        else:
            response["note"] = "No custom emojis found for this member"
        
        return response
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve member custom emojis: {str(e)}",
            "action": "get_members_custom_emoji",
            "member_id": id_member,
            "message": f"Failed to retrieve custom emojis for member {id_member}"
        }


@mcp.tool(
    "TRELLO_GET_MEMBERS_CUSTOM_STICKERS_BY_ID_MEMBER",
    description="Get member custom stickers. Retrieves a member's custom stickers, which are unique personalized stickers created by them, distinct from standard trello stickers.",
)
def TRELLO_GET_MEMBERS_CUSTOM_STICKERS_BY_ID_MEMBER(
    id_member: Annotated[str, "The ID of the member to get custom stickers for."],
    filter: Annotated[str, "The filter criteria for custom stickers (e.g., 'all', 'mine'). Defaults to all."] = "all"
):
    """Get member custom stickers. Retrieves a member's custom stickers, which are unique personalized stickers created by them, distinct from standard trello stickers."""
    err = _validate_required({"id_member": id_member}, ["id_member"])
    if err:
        return err
    
    try:
        # Get all custom stickers for the member
        endpoint = f"/members/{id_member}/customStickers"
        
        # Build query parameters
        params = {}
        if filter is not None:
            params["filter"] = filter
        
        # Make the API request
        result = trello_request("GET", endpoint, params=params)
        
        if not isinstance(result, list):
            return {
                "successful": False,
                "error": "Invalid custom stickers data received",
                "action": "get_members_custom_stickers",
                "member_id": id_member,
                "message": f"Failed to retrieve custom stickers for member {id_member}"
            }
        
        # Extract key information
        stickers_count = len(result)
        sticker_ids = [sticker.get("id") for sticker in result if sticker.get("id")]
        sticker_names = [sticker.get("name") for sticker in result if sticker.get("name")]
        
        response = {
            "successful": True,
            "data": result,
            "action": "get_members_custom_stickers",
            "member_id": id_member,
            "stickers_count": stickers_count,
            "sticker_ids": sticker_ids,
            "sticker_names": sticker_names,
            "message": f"Successfully retrieved {stickers_count} custom stickers for member {id_member}",
            "custom_stickers": result
        }
        
        # Add helpful information for using the stickers
        if sticker_ids:
            response["note"] = f"Use any of these sticker IDs with other sticker-related tools: {', '.join(sticker_ids[:5])}{'...' if len(sticker_ids) > 5 else ''}"
        else:
            response["note"] = "No custom stickers found for this member"
        
        return response
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve member custom stickers: {str(e)}",
            "action": "get_members_custom_stickers",
            "member_id": id_member,
            "message": f"Failed to retrieve custom stickers for member {id_member}"
        }


@mcp.tool(
    "TRELLO_GET_MEMBER_CUSTOM_STICKER",
    description="Get member custom sticker. Retrieves a specific custom sticker by id for a trello member; returns only sticker data (not its usage on cards/boards), with optional field selection.",
)
def TRELLO_GET_MEMBER_CUSTOM_STICKER(
    id_member: Annotated[str, "The ID of the member to get the custom sticker for."],
    id_custom_sticker: Annotated[str, "The ID of the custom sticker to retrieve."],
    fields: Annotated[str, "The fields to retrieve from the custom sticker (e.g., id, name, url, image). Defaults to all."] = "all"
):
    """Get member custom sticker. Retrieves a specific custom sticker by id for a trello member; returns only sticker data (not its usage on cards/boards), with optional field selection."""
    err = _validate_required({"id_member": id_member, "id_custom_sticker": id_custom_sticker}, ["id_member", "id_custom_sticker"])
    if err:
        return err
    
    try:
        # Get member custom sticker
        endpoint = f"/members/{id_member}/customStickers/{id_custom_sticker}"
        
        # Build query parameters
        params = {}
        if fields is not None:
            params["fields"] = fields
        
        # Make the API request
        result = trello_request("GET", endpoint, params=params)
        
        if not isinstance(result, dict):
            return {
                "successful": False,
                "error": "Invalid custom sticker data received",
                "action": "get_member_custom_sticker",
                "member_id": id_member,
                "custom_sticker_id": id_custom_sticker,
                "message": f"Failed to retrieve custom sticker {id_custom_sticker} for member {id_member}"
            }
        
        return {
            "successful": True,
            "data": result,
            "action": "get_member_custom_sticker",
            "member_id": id_member,
            "custom_sticker_id": id_custom_sticker,
            "sticker_name": result.get("name"),
            "sticker_url": result.get("url"),
            "sticker_image": result.get("image"),
            "message": f"Successfully retrieved custom sticker {id_custom_sticker} for member {id_member}",
            "custom_sticker": result
        }
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve member custom sticker: {str(e)}",
            "action": "get_member_custom_sticker",
            "member_id": id_member,
            "custom_sticker_id": id_custom_sticker,
            "message": f"Failed to retrieve custom sticker {id_custom_sticker} for member {id_member}"
        }


@mcp.tool(
    "TRELLO_GET_MEMBERS_ACTIONS_BY_ID_MEMBER",
    description="Get member actions by ID. Retrieves a list of actions for a specified trello member, allowing filtering by type, date, models, and control over output format and fields.",
)
def TRELLO_GET_MEMBERS_ACTIONS_BY_ID_MEMBER(
    id_member: Annotated[str, "The ID of the member to get actions for."],
    before: Annotated[str | None, "An action ID. Only return actions before this action."] = None,
    display: Annotated[str | None, "Whether to include display information."] = None,
    entities: Annotated[str | None, "Whether to include entities in the response."] = None,
    fields: Annotated[str, "The fields to retrieve from the actions (e.g., id, type, date, data). Defaults to all."] = "all",
    filter: Annotated[str, "The types of actions to return (e.g., commentCard, updateCard). Defaults to all."] = "all",
    format: Annotated[str, "The format for the returned actions. Defaults to list."] = "list",
    id_models: Annotated[str | None, "The IDs of models to include in the response."] = None,
    limit: Annotated[str, "The maximum number of actions to return. Defaults to 50."] = "50",
    member: Annotated[str | None, "Whether to include member information."] = None,
    member_creator: Annotated[str | None, "Whether to include member creator information."] = None,
    member_creator_fields: Annotated[str, "The fields to retrieve from member creators. Defaults to avatarHash, fullName, initials and username."] = "avatarHash,fullName,initials,username",
    member_fields: Annotated[str, "The fields to retrieve from members. Defaults to avatarHash, fullName, initials and username."] = "avatarHash,fullName,initials,username",
    page: Annotated[str, "The page of results to return. Defaults to 0."] = "0",
    since: Annotated[str | None, "An action ID. Only return actions after this action."] = None
):
    """Get member actions by ID. Retrieves a list of actions for a specified trello member, allowing filtering by type, date, models, and control over output format and fields."""
    err = _validate_required({"id_member": id_member}, ["id_member"])
    if err:
        return err
    
    try:
        # Get actions for the member
        endpoint = f"/members/{id_member}/actions"
        
        # Build query parameters
        params = {}
        if before is not None:
            params["before"] = before
        if display is not None:
            params["display"] = display
        if entities is not None:
            params["entities"] = entities
        if fields is not None:
            params["fields"] = fields
        if filter is not None:
            params["filter"] = filter
        if format is not None:
            params["format"] = format
        if id_models is not None:
            params["idModels"] = id_models
        if limit is not None:
            params["limit"] = limit
        if member is not None:
            params["member"] = member
        if member_creator is not None:
            params["memberCreator"] = member_creator
        if member_creator_fields is not None:
            params["memberCreator_fields"] = member_creator_fields
        if member_fields is not None:
            params["member_fields"] = member_fields
        if page is not None:
            params["page"] = page
        if since is not None:
            params["since"] = since
        
        # Make the API request
        result = trello_request("GET", endpoint, params=params)
        
        if not isinstance(result, list):
            return {
                "successful": False,
                "error": "Invalid actions data received",
                "action": "get_member_actions",
                "member_id": id_member,
                "message": f"Failed to retrieve actions for member {id_member}"
            }
        
        # Extract key information
        actions_count = len(result)
        action_types = list(set([action.get("type") for action in result if action.get("type")]))
        
        response = {
            "successful": True,
            "data": result,
            "action": "get_member_actions",
            "member_id": id_member,
            "actions_count": actions_count,
            "action_types": action_types,
            "message": f"Successfully retrieved {actions_count} actions for member {id_member}",
            "actions": result
        }
        
        # Add filtering information
        if filter != "all":
            response["filter_applied"] = filter
        if limit != "50":
            response["limit_applied"] = limit
        if page != "0":
            response["page_applied"] = page
        
        # Add helpful information
        if action_types:
            response["note"] = f"Action types found: {', '.join(action_types[:5])}{'...' if len(action_types) > 5 else ''}"
        else:
            response["note"] = "No actions found for this member"
        
        return response
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve member actions: {str(e)}",
            "action": "get_member_actions",
            "member_id": id_member,
            "message": f"Failed to retrieve actions for member {id_member}"
        }


@mcp.tool(
    "TRELLO_GET_MEMBERS_SAVED_SEARCHES_BY_ID_MEMBER",
    description="Get member saved searches. Retrieves all saved search queries for a trello member; this action only retrieves saved searches and does not execute them.",
)
def TRELLO_GET_MEMBERS_SAVED_SEARCHES_BY_ID_MEMBER(
    id_member: Annotated[str, "The ID of the member to get saved searches for."]
):
    """Get member saved searches. Retrieves all saved search queries for a trello member; this action only retrieves saved searches and does not execute them."""
    err = _validate_required({"id_member": id_member}, ["id_member"])
    if err:
        return err
    
    try:
        # Get all saved searches for the member
        endpoint = f"/members/{id_member}/savedSearches"
        
        # Make the API request
        result = trello_request("GET", endpoint)
        
        if not isinstance(result, list):
            return {
                "successful": False,
                "error": "Invalid saved searches data received",
                "action": "get_member_saved_searches",
                "member_id": id_member,
                "message": f"Failed to retrieve saved searches for member {id_member}"
            }
        
        # Extract key information
        searches_count = len(result)
        search_names = [search.get("name") for search in result if search.get("name")]
        search_queries = [search.get("query") for search in result if search.get("query")]
        
        response = {
            "successful": True,
            "data": result,
            "action": "get_member_saved_searches",
            "member_id": id_member,
            "searches_count": searches_count,
            "search_names": search_names,
            "search_queries": search_queries,
            "message": f"Successfully retrieved {searches_count} saved searches for member {id_member}",
            "saved_searches": result
        }
        
        # Add helpful information
        if search_names:
            response["note"] = f"Saved search names: {', '.join(search_names[:5])}{'...' if len(search_names) > 5 else ''}"
        else:
            response["note"] = "No saved searches found for this member"
        
        return response
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve member saved searches: {str(e)}",
            "action": "get_member_saved_searches",
            "member_id": id_member,
            "message": f"Failed to retrieve saved searches for member {id_member}"
        }


@mcp.tool(
    "TRELLO_GET_MEMBER_SAVED_SEARCH",
    description="Get Member Saved Search. Fetches the details of a specific saved search for a trello member; this does not execute the search.",
)
def TRELLO_GET_MEMBER_SAVED_SEARCH(
    id_member: Annotated[str, "The ID of the member to get the saved search for."],
    id_saved_search: Annotated[str, "The ID of the saved search to retrieve."]
):
    """Get Member Saved Search. Fetches the details of a specific saved search for a trello member; this does not execute the search."""
    err = _validate_required({"id_member": id_member, "id_saved_search": id_saved_search}, ["id_member", "id_saved_search"])
    if err:
        return err
    
    try:
        # Get specific saved search for the member
        endpoint = f"/members/{id_member}/savedSearches/{id_saved_search}"
        
        # Make the API request
        result = trello_request("GET", endpoint)
        
        if not isinstance(result, dict):
            return {
                "successful": False,
                "error": "Invalid saved search data received",
                "action": "get_member_saved_search",
                "member_id": id_member,
                "saved_search_id": id_saved_search,
                "message": f"Failed to retrieve saved search {id_saved_search} for member {id_member}"
            }
        
        return {
            "successful": True,
            "data": result,
            "action": "get_member_saved_search",
            "member_id": id_member,
            "saved_search_id": id_saved_search,
            "search_name": result.get("name"),
            "search_query": result.get("query"),
            "search_pos": result.get("pos"),
            "message": f"Successfully retrieved saved search {id_saved_search} for member {id_member}",
            "saved_search": result
        }
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve member saved search: {str(e)}",
            "action": "get_member_saved_search",
            "member_id": id_member,
            "saved_search_id": id_saved_search,
            "message": f"Failed to retrieve saved search {id_saved_search} for member {id_member}"
        }


@mcp.tool(
    "TRELLO_GET_MEMBERS_BOARD_BACKGROUNDS_BY_ID_MEMBER",
    description="Get member board backgrounds. Fetches the board backgrounds for a specified trello member.",
)
def TRELLO_GET_MEMBERS_BOARD_BACKGROUNDS_BY_ID_MEMBER(
    id_member: Annotated[str, "The ID of the member to get board backgrounds for."],
    filter: Annotated[str, "The filter criteria for board backgrounds (e.g., 'all', 'premium'). Defaults to all."] = "all"
):
    """Get member board backgrounds. Fetches the board backgrounds for a specified trello member."""
    err = _validate_required({"id_member": id_member}, ["id_member"])
    if err:
        return err
    
    try:
        # Get all board backgrounds for the member
        endpoint = f"/members/{id_member}/boardBackgrounds"
        
        # Build query parameters
        params = {}
        if filter is not None:
            params["filter"] = filter
        
        # Make the API request
        result = trello_request("GET", endpoint, params=params)
        
        if not isinstance(result, list):
            return {
                "successful": False,
                "error": "Invalid board backgrounds data received",
                "action": "get_member_board_backgrounds",
                "member_id": id_member,
                "message": f"Failed to retrieve board backgrounds for member {id_member}"
            }
        
        # Extract key information
        backgrounds_count = len(result)
        background_names = [bg.get("name") for bg in result if bg.get("name")]
        background_colors = [bg.get("color") for bg in result if bg.get("color")]
        
        response = {
            "successful": True,
            "data": result,
            "action": "get_member_board_backgrounds",
            "member_id": id_member,
            "backgrounds_count": backgrounds_count,
            "background_names": background_names,
            "background_colors": background_colors,
            "message": f"Successfully retrieved {backgrounds_count} board backgrounds for member {id_member}",
            "board_backgrounds": result
        }
        
        # Add helpful information
        if background_names:
            response["note"] = f"Board background names: {', '.join(background_names[:5])}{'...' if len(background_names) > 5 else ''}"
        else:
            response["note"] = "No board backgrounds found for this member"
        
        return response
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve member board backgrounds: {str(e)}",
            "action": "get_member_board_backgrounds",
            "member_id": id_member,
            "message": f"Failed to retrieve board backgrounds for member {id_member}"
        }


@mcp.tool(
    "TRELLO_GET_MEMBERS_BOARDS_BY_ID_MEMBER",
    description="Get member boards by id. Retrieves board-level details (not lists/cards) for trello boards associated with a member id or username, allowing extensive customization of the returned data.",
)
def TRELLO_GET_MEMBERS_BOARDS_BY_ID_MEMBER(
    id_member: Annotated[str, "The ID of the member to get boards for."],
    action_fields: Annotated[str, "The fields to retrieve from actions. Defaults to all."] = "all",
    actions: Annotated[str, "Whether to include actions in the response. Defaults to none."] = "none",
    actions_entities: Annotated[str, "Whether to include action entities. Defaults to false."] = "false",
    actions_format: Annotated[str, "The format for actions. Defaults to list."] = "list",
    actions_limit: Annotated[str, "The maximum number of actions to return. Defaults to 5."] = "5",
    actions_since: Annotated[str | None, "An action ID. Only return actions after this action."] = None,
    fields: Annotated[str, "The fields to retrieve from boards (e.g., id, name, desc, closed). Defaults to all."] = "all",
    filter: Annotated[str, "The filter criteria for boards (e.g., 'all', 'open', 'closed', 'starred'). Defaults to all."] = "all",
    lists: Annotated[str, "Whether to include lists in the response. Defaults to open."] = "open",
    memberships: Annotated[str, "Whether to include memberships in the response. Defaults to none."] = "none",
    organization: Annotated[str, "Whether to include organization information. Defaults to false."] = "false",
    organization_fields: Annotated[str, "The fields to retrieve from organizations. Defaults to name and displayName."] = "name,displayName"
):
    """Get member boards by id. Retrieves board-level details (not lists/cards) for trello boards associated with a member id or username, allowing extensive customization of the returned data."""
    err = _validate_required({"id_member": id_member}, ["id_member"])
    if err:
        return err
    
    try:
        # Get all boards for the member
        endpoint = f"/members/{id_member}/boards"
        
        # Build query parameters
        params = {}
        if action_fields is not None:
            params["action_fields"] = action_fields
        if actions is not None:
            params["actions"] = actions
        if actions_entities is not None:
            params["actions_entities"] = actions_entities
        if actions_format is not None:
            params["actions_format"] = actions_format
        if actions_limit is not None:
            params["actions_limit"] = actions_limit
        if actions_since is not None:
            params["actions_since"] = actions_since
        if fields is not None:
            params["fields"] = fields
        if filter is not None:
            params["filter"] = filter
        if lists is not None:
            params["lists"] = lists
        if memberships is not None:
            params["memberships"] = memberships
        if organization is not None:
            params["organization"] = organization
        if organization_fields is not None:
            params["organization_fields"] = organization_fields
        
        # Make the API request
        result = trello_request("GET", endpoint, params=params)
        
        if not isinstance(result, list):
            return {
                "successful": False,
                "error": "Invalid boards data received",
                "action": "get_member_boards",
                "member_id": id_member,
                "message": f"Failed to retrieve boards for member {id_member}"
            }
        
        # Extract key information
        boards_count = len(result)
        board_names = [board.get("name") for board in result if board.get("name")]
        board_ids = [board.get("id") for board in result if board.get("id")]
        open_boards = [board for board in result if not board.get("closed", False)]
        closed_boards = [board for board in result if board.get("closed", False)]
        starred_boards = [board for board in result if board.get("starred", False)]
        
        response = {
            "successful": True,
            "data": result,
            "action": "get_member_boards",
            "member_id": id_member,
            "boards_count": boards_count,
            "board_names": board_names,
            "board_ids": board_ids,
            "open_boards_count": len(open_boards),
            "closed_boards_count": len(closed_boards),
            "starred_boards_count": len(starred_boards),
            "message": f"Successfully retrieved {boards_count} boards for member {id_member}",
            "boards": result
        }
        
        # Add filter-specific information
        if filter == "open":
            response["note"] = "Showing only open (non-closed) boards"
        elif filter == "closed":
            response["note"] = "Showing only closed boards"
        elif filter == "starred":
            response["note"] = "Showing only starred boards"
        elif filter == "all":
            response["note"] = "Showing all boards (open, closed, and starred)"
        else:
            response["note"] = f"Boards filtered by criteria: {filter}"
        
        # Add helpful information
        if board_names:
            response["sample_board_names"] = board_names[:5]
            if len(board_names) > 5:
                response["note"] += f" | Sample board names: {', '.join(board_names[:5])}..."
            else:
                response["note"] += f" | Board names: {', '.join(board_names)}"
        
        return response
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve member boards: {str(e)}",
            "action": "get_member_boards",
            "member_id": id_member,
            "message": f"Failed to retrieve boards for member {id_member}"
        }


@mcp.tool(
    "TRELLO_MEMBER_GET_BOARDS_BY_ID_MEMBER",
    description="Get member boards by id. Deprecated: use `getmembersboardsbyidmember`; retrieves trello boards for a member (id/username).",
)
def TRELLO_MEMBER_GET_BOARDS_BY_ID_MEMBER(
    id_member: Annotated[str, "The ID of the member to get boards for."],
    action_fields: Annotated[str, "The fields to retrieve from actions. Defaults to all."] = "all",
    actions: Annotated[str, "Whether to include actions in the response. Defaults to none."] = "none",
    actions_entities: Annotated[str, "Whether to include action entities. Defaults to false."] = "false",
    actions_format: Annotated[str, "The format for actions. Defaults to list."] = "list",
    actions_limit: Annotated[str, "The maximum number of actions to return. Defaults to 5."] = "5",
    actions_since: Annotated[str | None, "An action ID. Only return actions after this action."] = None,
    fields: Annotated[str, "The fields to retrieve from boards (e.g., id, name, desc, closed). Defaults to all."] = "all",
    filter: Annotated[str, "The filter criteria for boards (e.g., 'all', 'open', 'closed', 'starred'). Defaults to all."] = "all",
    lists: Annotated[str, "Whether to include lists in the response. Defaults to open."] = "open",
    memberships: Annotated[str, "Whether to include memberships in the response. Defaults to none."] = "none",
    organization: Annotated[str, "Whether to include organization information. Defaults to false."] = "false",
    organization_fields: Annotated[str, "The fields to retrieve from organizations. Defaults to name and displayName."] = "name,displayName"
):
    """Get member boards by id. Deprecated: use `getmembersboardsbyidmember`; retrieves trello boards for a member (id/username)."""
    # This is a deprecated wrapper around TRELLO_GET_MEMBERS_BOARDS_BY_ID_MEMBER
    return TRELLO_GET_MEMBERS_BOARDS_BY_ID_MEMBER(
        id_member=id_member,
        action_fields=action_fields,
        actions=actions,
        actions_entities=actions_entities,
        actions_format=actions_format,
        actions_limit=actions_limit,
        actions_since=actions_since,
        fields=fields,
        filter=filter,
        lists=lists,
        memberships=memberships,
        organization=organization,
        organization_fields=organization_fields
    )


@mcp.tool(
    "TRELLO_GET_MEMBERS_BOARDS_BY_ID_MEMBER_BY_FILTER",
    description="Get member boards with filter. Retrieves a list of boards for a specific trello member, applying a filter such as 'open', 'starred', or 'all'.",
)
def TRELLO_GET_MEMBERS_BOARDS_BY_ID_MEMBER_BY_FILTER(
    id_member: Annotated[str, "The ID of the member to get boards for."],
    filter: Annotated[str, "The filter criteria for boards (e.g., 'open', 'closed', 'starred', 'all'). Defaults to open."] = "open"
):
    """Get member boards with filter. Retrieves a list of boards for a specific trello member, applying a filter such as 'open', 'starred', or 'all'."""
    err = _validate_required({"id_member": id_member}, ["id_member"])
    if err:
        return err
    
    try:
        # Get boards for the member with filter
        endpoint = f"/members/{id_member}/boards"
        
        # Build query parameters
        params = {
            "filter": filter
        }
        
        # Make the API request
        result = trello_request("GET", endpoint, params=params)
        
        if not isinstance(result, list):
            return {
                "successful": False,
                "error": "Invalid boards data received",
                "action": "get_member_boards_filtered",
                "member_id": id_member,
                "filter": filter,
                "message": f"Failed to retrieve boards with filter '{filter}' for member {id_member}"
            }
        
        # Extract key information
        boards_count = len(result)
        board_names = [board.get("name") for board in result if board.get("name")]
        board_ids = [board.get("id") for board in result if board.get("id")]
        open_boards = [board for board in result if not board.get("closed", False)]
        closed_boards = [board for board in result if board.get("closed", False)]
        starred_boards = [board for board in result if board.get("starred", False)]
        
        response = {
            "successful": True,
            "data": result,
            "action": "get_member_boards_filtered",
            "member_id": id_member,
            "filter": filter,
            "boards_count": boards_count,
            "board_names": board_names,
            "board_ids": board_ids,
            "open_boards_count": len(open_boards),
            "closed_boards_count": len(closed_boards),
            "starred_boards_count": len(starred_boards),
            "message": f"Successfully retrieved {boards_count} boards with filter '{filter}' for member {id_member}",
            "boards": result
        }
        
        # Add filter-specific information
        if filter == "open":
            response["note"] = "Showing only open (non-closed) boards"
        elif filter == "closed":
            response["note"] = "Showing only closed boards"
        elif filter == "starred":
            response["note"] = "Showing only starred boards"
        elif filter == "all":
            response["note"] = "Showing all boards (open, closed, and starred)"
        else:
            response["note"] = f"Boards filtered by criteria: {filter}"
        
        # Add helpful information
        if board_names:
            response["sample_board_names"] = board_names[:5]
            if len(board_names) > 5:
                response["note"] += f" | Sample board names: {', '.join(board_names[:5])}..."
            else:
                response["note"] += f" | Board names: {', '.join(board_names)}"
        
        return response
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve member boards: {str(e)}",
            "action": "get_member_boards_filtered",
            "member_id": id_member,
            "filter": filter,
            "message": f"Failed to retrieve boards with filter '{filter}' for member {id_member}"
        }


@mcp.tool(
    "TRELLO_MEMBER_GET_BOARDS",
    description="Get member boards with filter. Deprecated: retrieves a filtered list of boards for a trello member; use `get members boards by id member by filter` instead.",
)
def TRELLO_MEMBER_GET_BOARDS(
    id_member: Annotated[str, "The ID of the member to get boards for."],
    filter: Annotated[str, "The filter criteria for boards (e.g., 'open', 'closed', 'starred', 'all'). Defaults to open."] = "open"
):
    """Get member boards with filter. Deprecated: retrieves a filtered list of boards for a trello member; use `get members boards by id member by filter` instead."""
    # This is a deprecated wrapper around TRELLO_GET_MEMBERS_BOARDS_BY_ID_MEMBER_BY_FILTER
    return TRELLO_GET_MEMBERS_BOARDS_BY_ID_MEMBER_BY_FILTER(
        id_member=id_member,
        filter=filter
    )


@mcp.tool(
    "TRELLO_GET_MEMBERS_BOARDS_INVITED_BY_ID_MEMBER",
    description="Get member's invited boards. Retrieves trello boards to which a specific member has been invited but has not yet joined.",
)
def TRELLO_GET_MEMBERS_BOARDS_INVITED_BY_ID_MEMBER(
    id_member: Annotated[str, "The ID of the member to get invited boards for."],
    fields: Annotated[str, "The fields to retrieve from the invited boards (e.g., id, name, desc, closed). Defaults to all."] = "all"
):
    """Get member's invited boards. Retrieves trello boards to which a specific member has been invited but has not yet joined."""
    err = _validate_required({"id_member": id_member}, ["id_member"])
    if err:
        return err
    
    try:
        # Get invited boards for the member
        endpoint = f"/members/{id_member}/boardsInvited"
        
        # Build query parameters
        params = {}
        if fields is not None:
            params["fields"] = fields
        
        # Make the API request
        result = trello_request("GET", endpoint, params=params)
        
        if not isinstance(result, list):
            return {
                "successful": False,
                "error": "Invalid invited boards data received",
                "action": "get_member_invited_boards",
                "member_id": id_member,
                "message": f"Failed to retrieve invited boards for member {id_member}"
            }
        
        # Extract key information
        invited_boards_count = len(result)
        board_names = [board.get("name") for board in result if board.get("name")]
        board_ids = [board.get("id") for board in result if board.get("id")]
        board_urls = [board.get("url") for board in result if board.get("url")]
        
        response = {
            "successful": True,
            "data": result,
            "action": "get_member_invited_boards",
            "member_id": id_member,
            "invited_boards_count": invited_boards_count,
            "board_names": board_names,
            "board_ids": board_ids,
            "board_urls": board_urls,
            "message": f"Successfully retrieved {invited_boards_count} invited boards for member {id_member}",
            "invited_boards": result
        }
        
        # Add helpful information
        if board_names:
            response["note"] = f"Invited board names: {', '.join(board_names[:5])}{'...' if len(board_names) > 5 else ''}"
            response["sample_board_names"] = board_names[:5]
        else:
            response["note"] = "No pending board invitations found for this member"
        
        # Add invitation status information
        response["invitation_status"] = "pending"
        response["action_required"] = "Member needs to accept or decline these board invitations"
        
        return response
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve member invited boards: {str(e)}",
            "action": "get_member_invited_boards",
            "member_id": id_member,
            "message": f"Failed to retrieve invited boards for member {id_member}"
        }


@mcp.tool(
    "TRELLO_GET_MEMBERS_BOARDS_INVITED_BY_ID_MEMBER_BY_FIELD",
    description="Get member's invited board field. Retrieves a specific field from trello boards to which a member has been invited but not yet joined; returns an empty result for no pending invitations.",
)
def TRELLO_GET_MEMBERS_BOARDS_INVITED_BY_ID_MEMBER_BY_FIELD(
    id_member: Annotated[str, "The ID of the member to get invited board field for."],
    field: Annotated[str, "The specific field to retrieve from invited boards (e.g., id, name, desc, url)."]
):
    """Get member's invited board field. Retrieves a specific field from trello boards to which a member has been invited but not yet joined; returns an empty result for no pending invitations."""
    err = _validate_required({"id_member": id_member, "field": field}, ["id_member", "field"])
    if err:
        return err
    
    try:
        # Get invited boards for the member with specific field
        endpoint = f"/members/{id_member}/boardsInvited"
        
        # Build query parameters
        params = {
            "fields": field
        }
        
        # Make the API request
        result = trello_request("GET", endpoint, params=params)
        
        if not isinstance(result, list):
            return {
                "successful": False,
                "error": "Invalid invited boards data received",
                "action": "get_member_invited_board_field",
                "member_id": id_member,
                "field": field,
                "message": f"Failed to retrieve invited board field '{field}' for member {id_member}"
            }
        
        # Extract key information
        invited_boards_count = len(result)
        field_values = [board.get(field) for board in result if field in board]
        
        response = {
            "successful": True,
            "data": result,
            "action": "get_member_invited_board_field",
            "member_id": id_member,
            "field": field,
            "invited_boards_count": invited_boards_count,
            "field_values": field_values,
            "message": f"Successfully retrieved field '{field}' from {invited_boards_count} invited boards for member {id_member}",
            "invited_boards": result
        }
        
        # Add helpful information
        if field_values:
            response["note"] = f"Field '{field}' values: {', '.join([str(v) for v in field_values[:5]])}{'...' if len(field_values) > 5 else ''}"
            response["sample_field_values"] = field_values[:5]
        else:
            response["note"] = f"No pending board invitations found for this member, or field '{field}' not present in any invited boards"
        
        # Add invitation status information
        response["invitation_status"] = "pending"
        response["action_required"] = "Member needs to accept or decline these board invitations"
        
        return response
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve member invited board field: {str(e)}",
            "action": "get_member_invited_board_field",
            "member_id": id_member,
            "field": field,
            "message": f"Failed to retrieve invited board field '{field}' for member {id_member}"
        }


@mcp.tool(
    "TRELLO_GET_MEMBERS_BOARD_STARS_BY_ID_MEMBER",
    description="Get member board stars. Fetches only the boards a specific trello member has starred, identified by their id or username.",
)
def TRELLO_GET_MEMBERS_BOARD_STARS_BY_ID_MEMBER(
    id_member: Annotated[str, "The ID of the member to get starred boards for."]
):
    """Get member board stars. Fetches only the boards a specific trello member has starred, identified by their id or username."""
    err = _validate_required({"id_member": id_member}, ["id_member"])
    if err:
        return err
    
    try:
        # Get board stars for the member
        endpoint = f"/members/{id_member}/boardStars"
        
        # Make the API request
        result = trello_request("GET", endpoint)
        
        if not isinstance(result, list):
            return {
                "successful": False,
                "error": "Invalid starred boards data received",
                "action": "get_member_board_stars",
                "member_id": id_member,
                "message": f"Failed to retrieve starred boards for member {id_member}"
            }
        
        # Extract key information
        board_stars_count = len(result)
        board_star_ids = [star.get("id") for star in result if star.get("id")]
        board_ids = [star.get("idBoard") for star in result if star.get("idBoard")]
        star_positions = [star.get("pos") for star in result if star.get("pos")]
        star_colors = [star.get("color") for star in result if star.get("color")]
        
        response = {
            "successful": True,
            "data": result,
            "action": "get_member_board_stars",
            "member_id": id_member,
            "board_stars_count": board_stars_count,
            "board_star_ids": board_star_ids,
            "board_ids": board_ids,
            "star_positions": star_positions,
            "star_colors": star_colors,
            "message": f"Successfully retrieved {board_stars_count} board stars for member {id_member}",
            "board_stars": result
        }
        
        # Add helpful information
        if board_star_ids:
            response["note"] = f"Board star IDs: {', '.join(board_star_ids[:5])}{'...' if len(board_star_ids) > 5 else ''}"
            response["sample_board_star_ids"] = board_star_ids[:5]
        else:
            response["note"] = "No board stars found for this member"
        
        # Add star status information
        response["star_status"] = "starred"
        response["description"] = "These are board star relationships that the member has created"
        
        return response
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve member board stars: {str(e)}",
            "action": "get_member_board_stars",
            "member_id": id_member,
            "message": f"Failed to retrieve starred boards for member {id_member}"
        }


@mcp.tool(
    "TRELLO_GET_MEMBERS_BOARD_STARS_BY_ID_MEMBER_BY_ID_BOARD_STAR",
    description="Get member board star. Retrieves detailed information about a specific board star (a trello board marked as a favorite) for a given trello member.",
)
def TRELLO_GET_MEMBERS_BOARD_STARS_BY_ID_MEMBER_BY_ID_BOARD_STAR(
    id_member: Annotated[str, "The ID of the member to get the board star for."],
    id_board_star: Annotated[str, "The ID of the board star to retrieve."]
):
    """Get member board star. Retrieves detailed information about a specific board star (a trello board marked as a favorite) for a given trello member."""
    err = _validate_required({"id_member": id_member, "id_board_star": id_board_star}, ["id_member", "id_board_star"])
    if err:
        return err
    
    try:
        # Get specific board star for the member
        endpoint = f"/members/{id_member}/boardStars/{id_board_star}"
        
        # Make the API request
        result = trello_request("GET", endpoint)
        
        if not isinstance(result, dict):
            return {
                "successful": False,
                "error": "Invalid board star data received",
                "action": "get_member_board_star",
                "member_id": id_member,
                "board_star_id": id_board_star,
                "message": f"Failed to retrieve board star {id_board_star} for member {id_member}"
            }
        
        # Extract key information
        board_id = result.get("idBoard")
        board_name = result.get("name")
        star_position = result.get("pos")
        star_color = result.get("color")
        
        response = {
            "successful": True,
            "data": result,
            "action": "get_member_board_star",
            "member_id": id_member,
            "board_star_id": id_board_star,
            "board_id": board_id,
            "board_name": board_name,
            "star_position": star_position,
            "star_color": star_color,
            "message": f"Successfully retrieved board star {id_board_star} for member {id_member}",
            "board_star": result
        }
        
        # Add helpful information
        if board_name:
            response["note"] = f"Board star for '{board_name}' (ID: {board_id})"
        else:
            response["note"] = f"Board star details for board ID: {board_id}"
        
        # Add star status information
        response["star_status"] = "starred"
        response["description"] = "This is a board that the member has marked as a favorite"
        
        return response
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve member board star: {str(e)}",
            "action": "get_member_board_star",
            "member_id": id_member,
            "board_star_id": id_board_star,
            "message": f"Failed to retrieve board star {id_board_star} for member {id_member}"
        }


@mcp.tool(
    "TRELLO_GET_MEMBERS_BY_ID_MEMBER_BY_FIELD",
    description="Get member field by ID. Efficiently retrieves a specific field (e.g., fullname, username, bio) of a trello member using their id or username, without fetching the entire member profile.",
)
def TRELLO_GET_MEMBERS_BY_ID_MEMBER_BY_FIELD(
    id_member: Annotated[str, "The ID or username of the member to get the field from."],
    field: Annotated[str, "The specific field to retrieve from the member (e.g., fullName, username, bio, email, avatarHash, initials)."]
):
    """Get member field by ID. Efficiently retrieves a specific field (e.g., fullname, username, bio) of a trello member using their id or username, without fetching the entire member profile."""
    err = _validate_required({"id_member": id_member, "field": field}, ["id_member", "field"])
    if err:
        return err
    
    try:
        # Get specific field from member
        endpoint = f"/members/{id_member}"
        
        # Build query parameters
        params = {
            "fields": field
        }
        
        # Make the API request
        result = trello_request("GET", endpoint, params=params)
        
        if not isinstance(result, dict):
            return {
                "successful": False,
                "error": "Invalid member data received",
                "action": "get_member_field",
                "member_id": id_member,
                "field": field,
                "message": f"Failed to retrieve member field '{field}' for member {id_member}"
            }
        
        # Extract the specific field value
        field_value = result.get(field)
        
        response = {
            "successful": True,
            "data": {field: field_value},
            "action": "get_member_field",
            "member_id": id_member,
            "field": field,
            "field_value": field_value,
            "message": f"Successfully retrieved member field '{field}' for member {id_member}",
            "member_field": field_value
        }
        
        # Add helpful information based on field type
        if field == "fullName":
            response["note"] = f"Full name: {field_value}"
        elif field == "username":
            response["note"] = f"Username: @{field_value}"
        elif field == "email":
            response["note"] = f"Email address: {field_value}"
        elif field == "bio":
            response["note"] = f"Bio: {field_value[:100]}{'...' if field_value and len(field_value) > 100 else ''}"
        elif field == "avatarHash":
            response["note"] = f"Avatar hash: {field_value}"
        elif field == "initials":
            response["note"] = f"Initials: {field_value}"
        else:
            response["note"] = f"Field '{field}' value: {field_value}"
        
        # Add field type information
        if field_value is None:
            response["field_status"] = "not_set"
            response["description"] = f"The field '{field}' is not set for this member"
        else:
            response["field_status"] = "set"
            response["description"] = f"The field '{field}' is available for this member"
        
        return response
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve member field: {str(e)}",
            "action": "get_member_field",
            "member_id": id_member,
            "field": field,
            "message": f"Failed to retrieve member field '{field}' for member {id_member}"
        }


@mcp.tool(
    "TRELLO_GET_MEMBERS_CARDS_BY_ID_MEMBER_BY_FILTER",
    description="Get member cards by filter. Retrieves cards for a trello member, applying a filter that must be a trello-recognized card filter.",
)
def TRELLO_GET_MEMBERS_CARDS_BY_ID_MEMBER_BY_FILTER(
    id_member: Annotated[str, "The ID or username of the member to get cards for."],
    filter: Annotated[str, "The filter criteria for cards (e.g., 'open', 'closed', 'all', 'visible', 'pinned', 'unpinned', 'recentlyViewed', 'starred', 'unstarred')."]
):
    """Get member cards by filter. Retrieves cards for a trello member, applying a filter that must be a trello-recognized card filter."""
    err = _validate_required({"id_member": id_member, "filter": filter}, ["id_member", "filter"])
    if err:
        return err
    
    try:
        # Get cards for the member with filter
        endpoint = f"/members/{id_member}/cards"
        
        # Build query parameters
        params = {
            "filter": filter
        }
        
        # Make the API request
        result = trello_request("GET", endpoint, params=params)
        
        if not isinstance(result, list):
            return {
                "successful": False,
                "error": "Invalid cards data received",
                "action": "get_member_cards_filtered",
                "member_id": id_member,
                "filter": filter,
                "message": f"Failed to retrieve cards with filter '{filter}' for member {id_member}"
            }
        
        # Extract key information
        cards_count = len(result)
        open_cards = [card for card in result if not card.get("closed", False)]
        closed_cards = [card for card in result if card.get("closed", False)]
        card_names = [card.get("name") for card in result if card.get("name")]
        card_ids = [card.get("id") for card in result if card.get("id")]
        
        response = {
            "successful": True,
            "data": result,
            "action": "get_member_cards_filtered",
            "member_id": id_member,
            "filter": filter,
            "cards_count": cards_count,
            "open_cards_count": len(open_cards),
            "closed_cards_count": len(closed_cards),
            "card_names": card_names,
            "card_ids": card_ids,
            "message": f"Successfully retrieved {cards_count} cards with filter '{filter}' for member {id_member}",
            "cards": result
        }
        
        # Add filter-specific information
        if filter == "open":
            response["note"] = "Showing only open (non-closed) cards"
            response["filter_description"] = "Cards that are currently active and not archived"
        elif filter == "closed":
            response["note"] = "Showing only closed cards"
            response["filter_description"] = "Cards that have been archived or closed"
        elif filter == "all":
            response["note"] = "Showing all cards (open and closed)"
            response["filter_description"] = "All cards accessible to the member"
        elif filter == "visible":
            response["note"] = "Showing only visible cards"
            response["filter_description"] = "Cards that are visible to the member"
        elif filter == "pinned":
            response["note"] = "Showing only pinned cards"
            response["filter_description"] = "Cards that have been pinned by the member"
        elif filter == "unpinned":
            response["note"] = "Showing only unpinned cards"
            response["filter_description"] = "Cards that are not pinned"
        elif filter == "recentlyViewed":
            response["note"] = "Showing recently viewed cards"
            response["filter_description"] = "Cards that the member has viewed recently"
        elif filter == "starred":
            response["note"] = "Showing only starred cards"
            response["filter_description"] = "Cards that the member has starred"
        elif filter == "unstarred":
            response["note"] = "Showing only unstarred cards"
            response["filter_description"] = "Cards that the member has not starred"
        else:
            response["note"] = f"Cards filtered by criteria: {filter}"
            response["filter_description"] = f"Cards matching the '{filter}' filter criteria"
        
        # Add helpful information
        if card_names:
            response["sample_card_names"] = card_names[:5]
            response["sample_card_ids"] = card_ids[:5]
        else:
            response["note"] = f"No cards found matching filter '{filter}' for this member"
        
        return response
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve member cards: {str(e)}",
            "action": "get_member_cards_filtered",
            "member_id": id_member,
            "filter": filter,
            "message": f"Failed to retrieve cards with filter '{filter}' for member {id_member}"
        }


@mcp.tool(
    "TRELLO_GET_MEMBERS_DELTAS_BY_ID_MEMBER",
    description="Get member deltas by ID. Retrieves a chronological list of all changes (deltas) made by a specific trello member, including modifications to boards, lists, and cards, to audit activity or sync data.",
)
def TRELLO_GET_MEMBERS_DELTAS_BY_ID_MEMBER(
    id_member: Annotated[str, "The ID or username of the member to get deltas for."],
    ix_last_update: Annotated[str, "The index of the last update to start from (0 for all changes)."],
    tags: Annotated[str, "Comma-separated list of tags to filter deltas (e.g., 'board,list,card,action,member')."]
):
    """Get member deltas by ID. Retrieves a chronological list of all changes (deltas) made by a specific trello member, including modifications to boards, lists, and cards, to audit activity or sync data."""
    err = _validate_required({"id_member": id_member, "ix_last_update": ix_last_update, "tags": tags}, ["id_member", "ix_last_update", "tags"])
    if err:
        return err
    
    try:
        # Get member deltas
        endpoint = f"/members/{id_member}/deltas"
        
        # Build query parameters
        params = {
            "ixLastUpdate": ix_last_update,
            "tags": tags
        }
        
        # Make the API request
        result = trello_request("GET", endpoint, params=params)
        
        if not isinstance(result, dict):
            return {
                "successful": False,
                "error": "Invalid deltas data received",
                "action": "get_member_deltas",
                "member_id": id_member,
                "ix_last_update": ix_last_update,
                "tags": tags,
                "message": f"Failed to retrieve deltas for member {id_member}"
            }
        
        # Extract key information
        deltas = result.get("deltas", [])
        deltas_count = len(deltas)
        last_update = result.get("ixLastUpdate")
        tags_list = tags.split(",") if tags else []
        
        # Analyze delta types
        delta_types = {}
        for delta in deltas:
            delta_type = delta.get("type", "unknown")
            delta_types[delta_type] = delta_types.get(delta_type, 0) + 1
        
        response = {
            "successful": True,
            "data": result,
            "action": "get_member_deltas",
            "member_id": id_member,
            "ix_last_update": ix_last_update,
            "tags": tags,
            "deltas_count": deltas_count,
            "last_update_index": last_update,
            "delta_types": delta_types,
            "message": f"Successfully retrieved {deltas_count} deltas for member {id_member}",
            "deltas": deltas
        }
        
        # Add helpful information
        if deltas_count > 0:
            response["note"] = f"Retrieved {deltas_count} changes since update index {ix_last_update}"
            response["filtered_tags"] = tags_list
            response["delta_type_breakdown"] = delta_types
        else:
            response["note"] = f"No changes found since update index {ix_last_update}"
        
        # Add sync information
        response["sync_info"] = {
            "last_update_index": last_update,
            "next_sync_start": last_update if last_update else "0",
            "total_changes": deltas_count,
            "filtered_by_tags": tags_list
        }
        
        # Add audit information
        response["audit_info"] = {
            "member_id": id_member,
            "changes_since": ix_last_update,
            "change_types": list(delta_types.keys()),
            "total_changes": deltas_count
        }
        
        return response
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve member deltas: {str(e)}",
            "action": "get_member_deltas",
            "member_id": id_member,
            "ix_last_update": ix_last_update,
            "tags": tags,
            "message": f"Failed to retrieve deltas for member {id_member}"
        }


@mcp.tool(
    "TRELLO_GET_MEMBERS_NOTIFICATIONS_BY_ID_MEMBER",
    description="Get member notifications by id. Retrieves notifications for a trello member, specified by their id or username, with options for filtering and pagination.",
)
def TRELLO_GET_MEMBERS_NOTIFICATIONS_BY_ID_MEMBER(
    id_member: Annotated[str, "The ID or username of the member to get notifications for."],
    before: Annotated[str | None, "An action ID. Only return notifications before this action."] = None,
    display: Annotated[str | None, "Whether to include display information."] = None,
    entities: Annotated[str | None, "Whether to include entities in the response."] = None,
    fields: Annotated[str, "The fields to retrieve from the notifications (e.g., id, type, date, data). Defaults to all."] = "all",
    filter: Annotated[str, "The types of notifications to return (e.g., 'all', 'unread', 'read'). Defaults to all."] = "all",
    limit: Annotated[str, "The maximum number of notifications to return. Defaults to 50."] = "50",
    member_creator: Annotated[str | None, "Whether to include member creator information."] = None,
    member_creator_fields: Annotated[str, "The fields to retrieve from member creators. Defaults to avatarHash, fullName, initials and username."] = "avatarHash,fullName,initials,username",
    page: Annotated[str, "The page of results to return. Defaults to 0."] = "0",
    read_filter: Annotated[str, "Filter by read status (e.g., 'all', 'read', 'unread'). Defaults to all."] = "all",
    since: Annotated[str | None, "An action ID. Only return notifications after this action."] = None
):
    """Get member notifications by id. Retrieves notifications for a trello member, specified by their id or username, with options for filtering and pagination."""
    err = _validate_required({"id_member": id_member}, ["id_member"])
    if err:
        return err
    
    try:
        # Get notifications for the member
        endpoint = f"/members/{id_member}/notifications"
        
        # Build query parameters
        params = {}
        if before is not None:
            params["before"] = before
        if display is not None:
            params["display"] = display
        if entities is not None:
            params["entities"] = entities
        if fields is not None:
            params["fields"] = fields
        if filter is not None:
            params["filter"] = filter
        if limit is not None:
            params["limit"] = limit
        if member_creator is not None:
            params["memberCreator"] = member_creator
        if member_creator_fields is not None:
            params["memberCreator_fields"] = member_creator_fields
        if page is not None:
            params["page"] = page
        if read_filter is not None:
            params["read_filter"] = read_filter
        if since is not None:
            params["since"] = since
        
        # Make the API request
        result = trello_request("GET", endpoint, params=params)
        
        if not isinstance(result, list):
            return {
                "successful": False,
                "error": "Invalid notifications data received",
                "action": "get_member_notifications",
                "member_id": id_member,
                "message": f"Failed to retrieve notifications for member {id_member}"
            }
        
        # Extract key information
        notifications_count = len(result)
        unread_count = len([n for n in result if not n.get("read", True)])
        read_count = len([n for n in result if n.get("read", False)])
        notification_types = list(set([n.get("type") for n in result if n.get("type")]))
        
        response = {
            "successful": True,
            "data": result,
            "action": "get_member_notifications",
            "member_id": id_member,
            "notifications_count": notifications_count,
            "unread_count": unread_count,
            "read_count": read_count,
            "notification_types": notification_types,
            "message": f"Successfully retrieved {notifications_count} notifications for member {id_member}",
            "notifications": result
        }
        
        # Add filtering information
        if filter != "all":
            response["filter_applied"] = filter
        if read_filter != "all":
            response["read_filter_applied"] = read_filter
        if limit != "50":
            response["limit_applied"] = limit
        if page != "0":
            response["page_applied"] = page
        
        # Add helpful information
        if notification_types:
            response["note"] = f"Notification types found: {', '.join(notification_types[:5])}{'...' if len(notification_types) > 5 else ''}"
        else:
            response["note"] = "No notifications found for this member"
        
        # Add read status information
        if unread_count > 0:
            response["unread_info"] = f"{unread_count} unread notifications"
        if read_count > 0:
            response["read_info"] = f"{read_count} read notifications"
        
        # Add pagination information
        response["pagination_info"] = {
            "current_page": int(page),
            "notifications_per_page": int(limit),
            "total_notifications": notifications_count,
            "has_more": notifications_count == int(limit)
        }
        
        return response
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve member notifications: {str(e)}",
            "action": "get_member_notifications",
            "member_id": id_member,
            "message": f"Failed to retrieve notifications for member {id_member}"
        }


@mcp.tool(
    "TRELLO_GET_MEMBERS_NOTIFICATIONS_BY_ID_MEMBER_BY_FILTER",
    description="Get member notifications by filter. Retrieves a list of a trello member's notifications, filtered by specified types.",
)
def TRELLO_GET_MEMBERS_NOTIFICATIONS_BY_ID_MEMBER_BY_FILTER(
    id_member: Annotated[str, "The ID or username of the member to get notifications for."],
    filter: Annotated[str, "The types of notifications to return (e.g., 'all', 'unread', 'read', 'commentCard', 'addedToCard', 'changeCard')."]
):
    """Get member notifications by filter. Retrieves a list of a trello member's notifications, filtered by specified types."""
    err = _validate_required({"id_member": id_member, "filter": filter}, ["id_member", "filter"])
    if err:
        return err
    
    try:
        # Get notifications for the member with filter
        endpoint = f"/members/{id_member}/notifications"
        
        # Build query parameters
        params = {
            "filter": filter
        }
        
        # Make the API request
        result = trello_request("GET", endpoint, params=params)
        
        if not isinstance(result, list):
            return {
                "successful": False,
                "error": "Invalid notifications data received",
                "action": "get_member_notifications_filtered",
                "member_id": id_member,
                "filter": filter,
                "message": f"Failed to retrieve notifications with filter '{filter}' for member {id_member}"
            }
        
        # Extract key information
        notifications_count = len(result)
        unread_count = len([n for n in result if not n.get("read", True)])
        read_count = len([n for n in result if n.get("read", False)])
        notification_types = list(set([n.get("type") for n in result if n.get("type")]))
        
        response = {
            "successful": True,
            "data": result,
            "action": "get_member_notifications_filtered",
            "member_id": id_member,
            "filter": filter,
            "notifications_count": notifications_count,
            "unread_count": unread_count,
            "read_count": read_count,
            "notification_types": notification_types,
            "message": f"Successfully retrieved {notifications_count} notifications with filter '{filter}' for member {id_member}",
            "notifications": result
        }
        
        # Add filter-specific information
        if filter == "all":
            response["note"] = "Showing all notifications"
            response["filter_description"] = "All notifications for the member"
        elif filter == "unread":
            response["note"] = "Showing only unread notifications"
            response["filter_description"] = "Notifications that have not been read"
        elif filter == "read":
            response["note"] = "Showing only read notifications"
            response["filter_description"] = "Notifications that have been read"
        elif filter == "commentCard":
            response["note"] = "Showing only card comment notifications"
            response["filter_description"] = "Notifications about comments on cards"
        elif filter == "addedToCard":
            response["note"] = "Showing only 'added to card' notifications"
            response["filter_description"] = "Notifications about being added to cards"
        elif filter == "removedFromCard":
            response["note"] = "Showing only 'removed from card' notifications"
            response["filter_description"] = "Notifications about being removed from cards"
        elif filter == "addedToBoard":
            response["note"] = "Showing only 'added to board' notifications"
            response["filter_description"] = "Notifications about being added to boards"
        elif filter == "removedFromBoard":
            response["note"] = "Showing only 'removed from board' notifications"
            response["filter_description"] = "Notifications about being removed from boards"
        elif filter == "changeCard":
            response["note"] = "Showing only card change notifications"
            response["filter_description"] = "Notifications about changes to cards"
        elif filter == "closeCard":
            response["note"] = "Showing only card close notifications"
            response["filter_description"] = "Notifications about cards being closed"
        elif filter == "reopenCard":
            response["note"] = "Showing only card reopen notifications"
            response["filter_description"] = "Notifications about cards being reopened"
        else:
            response["note"] = f"Notifications filtered by type: {filter}"
            response["filter_description"] = f"Notifications matching the '{filter}' filter"
        
        # Add helpful information
        if notification_types:
            response["note"] = f"Notification types found: {', '.join(notification_types[:5])}{'...' if len(notification_types) > 5 else ''}"
        else:
            response["note"] = f"No notifications found matching filter '{filter}' for this member"
        
        # Add read status information
        if unread_count > 0:
            response["unread_info"] = f"{unread_count} unread notifications"
        if read_count > 0:
            response["read_info"] = f"{read_count} read notifications"
        
        # Add filter analysis
        response["filter_analysis"] = {
            "applied_filter": filter,
            "total_matching": notifications_count,
            "unread_matching": unread_count,
            "read_matching": read_count,
            "types_found": notification_types
        }
        
        return response
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve member notifications: {str(e)}",
            "action": "get_member_notifications_filtered",
            "member_id": id_member,
            "filter": filter,
            "message": f"Failed to retrieve notifications with filter '{filter}' for member {id_member}"
        }


@mcp.tool(
    "TRELLO_GET_MEMBERS_ORGANIZATIONS_BY_ID_MEMBER",
    description="Get a specified member's organizations. Fetches organizations a specific trello member belongs to; the idmember must be an id or username of an existing trello member.",
)
def TRELLO_GET_MEMBERS_ORGANIZATIONS_BY_ID_MEMBER(
    id_member: Annotated[str, "The ID or username of the member to get organizations for."],
    fields: Annotated[str, "The fields to retrieve from the organizations (e.g., id, name, displayName, desc, descData, url, website, logoHash, products, powerUps, prefs, billableMemberCount, invitations, invited, limits, memberships, premiumFeatures). Defaults to all."] = "all",
    filter: Annotated[str, "The filter criteria for organizations (e.g., 'all', 'members', 'public', 'private'). Defaults to all."] = "all",
    paid_account: Annotated[str | None, "Whether to filter by paid account status (e.g., 'true', 'false')."] = None
):
    """Get a specified member's organizations. Fetches organizations a specific trello member belongs to; the idmember must be an id or username of an existing trello member."""
    err = _validate_required({"id_member": id_member}, ["id_member"])
    if err:
        return err
    
    try:
        # Get organizations for the member
        endpoint = f"/members/{id_member}/organizations"
        
        # Build query parameters
        params = {}
        if fields is not None:
            params["fields"] = fields
        if filter is not None:
            params["filter"] = filter
        if paid_account is not None:
            params["paid_account"] = paid_account
        
        # Make the API request
        result = trello_request("GET", endpoint, params=params)
        
        if not isinstance(result, list):
            return {
                "successful": False,
                "error": "Invalid organizations data received",
                "action": "get_member_organizations",
                "member_id": id_member,
                "message": f"Failed to retrieve organizations for member {id_member}"
            }
        
        # Extract key information
        organizations_count = len(result)
        organization_ids = [org.get("id") for org in result if org.get("id")]
        organization_names = [org.get("name") for org in result if org.get("name")]
        organization_display_names = [org.get("displayName") for org in result if org.get("displayName")]
        
        # Analyze organization types
        public_orgs = [org for org in result if org.get("prefs", {}).get("permissionLevel") == "public"]
        private_orgs = [org for org in result if org.get("prefs", {}).get("permissionLevel") == "private"]
        paid_orgs = [org for org in result if org.get("paid_account", False)]
        free_orgs = [org for org in result if not org.get("paid_account", False)]
        
        response = {
            "successful": True,
            "data": result,
            "action": "get_member_organizations",
            "member_id": id_member,
            "organizations_count": organizations_count,
            "organization_ids": organization_ids,
            "organization_names": organization_names,
            "organization_display_names": organization_display_names,
            "message": f"Successfully retrieved {organizations_count} organizations for member {id_member}",
            "organizations": result
        }
        
        # Add organization analysis
        response["organization_analysis"] = {
            "total_organizations": organizations_count,
            "public_organizations": len(public_orgs),
            "private_organizations": len(private_orgs),
            "paid_organizations": len(paid_orgs),
            "free_organizations": len(free_orgs)
        }
        
        # Add filter information
        if filter != "all":
            response["filter_applied"] = filter
            response["filter_description"] = f"Organizations filtered by: {filter}"
        
        if paid_account is not None:
            response["paid_account_filter"] = paid_account
            response["paid_account_description"] = f"Organizations filtered by paid account status: {paid_account}"
        
        # Add helpful information
        if organization_names:
            response["note"] = f"Organization names: {', '.join(organization_names[:5])}{'...' if len(organization_names) > 5 else ''}"
        else:
            response["note"] = "No organizations found for this member"
        
        # Add organization details
        if public_orgs:
            response["public_orgs"] = public_orgs
            response["public_org_names"] = [org.get("name") for org in public_orgs]
        
        if private_orgs:
            response["private_orgs"] = private_orgs
            response["private_org_names"] = [org.get("name") for org in private_orgs]
        
        if paid_orgs:
            response["paid_orgs"] = paid_orgs
            response["paid_org_names"] = [org.get("name") for org in paid_orgs]
        
        if free_orgs:
            response["free_orgs"] = free_orgs
            response["free_org_names"] = [org.get("name") for org in free_orgs]
        
        # Add organization summary
        response["organization_summary"] = {
            "total": organizations_count,
            "public": len(public_orgs),
            "private": len(private_orgs),
            "paid": len(paid_orgs),
            "free": len(free_orgs)
        }
        
        return response
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve member organizations: {str(e)}",
            "action": "get_member_organizations",
            "member_id": id_member,
            "message": f"Failed to retrieve organizations for member {id_member}"
        }


@mcp.tool(
    "TRELLO_GET_MEMBERS_ORGANIZATIONS_BY_ID_MEMBER_BY_FILTER",
    description="Get member organizations by filter. Fetches a list of organizations a specific trello member belongs to, using a filter to narrow down the results.",
)
def TRELLO_GET_MEMBERS_ORGANIZATIONS_BY_ID_MEMBER_BY_FILTER(
    id_member: Annotated[str, "The ID or username of the member to get organizations for."],
    filter: Annotated[str, "The filter criteria for organizations (e.g., 'all', 'members', 'public', 'private', 'paid', 'free')."]
):
    """Get member organizations by filter. Fetches a list of organizations a specific trello member belongs to, using a filter to narrow down the results."""
    err = _validate_required({"id_member": id_member, "filter": filter}, ["id_member", "filter"])
    if err:
        return err
    
    try:
        # Get organizations for the member with filter
        endpoint = f"/members/{id_member}/organizations"
        
        # Build query parameters
        params = {
            "filter": filter
        }
        
        # Make the API request
        result = trello_request("GET", endpoint, params=params)
        
        if not isinstance(result, list):
            return {
                "successful": False,
                "error": "Invalid organizations data received",
                "action": "get_member_organizations_filtered",
                "member_id": id_member,
                "filter": filter,
                "message": f"Failed to retrieve organizations with filter '{filter}' for member {id_member}"
            }
        
        # Extract key information
        organizations_count = len(result)
        organization_ids = [org.get("id") for org in result if org.get("id")]
        organization_names = [org.get("name") for org in result if org.get("name")]
        organization_display_names = [org.get("displayName") for org in result if org.get("displayName")]
        
        # Analyze organization types
        public_orgs = [org for org in result if org.get("prefs", {}).get("permissionLevel") == "public"]
        private_orgs = [org for org in result if org.get("prefs", {}).get("permissionLevel") == "private"]
        paid_orgs = [org for org in result if org.get("paid_account", False)]
        free_orgs = [org for org in result if not org.get("paid_account", False)]
        
        response = {
            "successful": True,
            "data": result,
            "action": "get_member_organizations_filtered",
            "member_id": id_member,
            "filter": filter,
            "organizations_count": organizations_count,
            "organization_ids": organization_ids,
            "organization_names": organization_names,
            "organization_display_names": organization_display_names,
            "message": f"Successfully retrieved {organizations_count} organizations with filter '{filter}' for member {id_member}",
            "organizations": result
        }
        
        # Add filter-specific information
        if filter == "all":
            response["note"] = "Showing all organizations"
            response["filter_description"] = "All organizations the member belongs to"
        elif filter == "members":
            response["note"] = "Showing organizations where user is a member"
            response["filter_description"] = "Organizations where the user has member-level access"
        elif filter == "public":
            response["note"] = "Showing only public organizations"
            response["filter_description"] = "Public organizations visible to all Trello users"
        elif filter == "private":
            response["note"] = "Showing only private organizations"
            response["filter_description"] = "Private organizations visible only to members"
        elif filter == "paid":
            response["note"] = "Showing only paid organizations"
            response["filter_description"] = "Organizations with paid Trello plans"
        elif filter == "free":
            response["note"] = "Showing only free organizations"
            response["filter_description"] = "Organizations using free Trello plans"
        else:
            response["note"] = f"Organizations filtered by: {filter}"
            response["filter_description"] = f"Organizations matching the '{filter}' filter"
        
        # Add organization analysis
        response["organization_analysis"] = {
            "applied_filter": filter,
            "total_matching": organizations_count,
            "public_matching": len(public_orgs),
            "private_matching": len(private_orgs),
            "paid_matching": len(paid_orgs),
            "free_matching": len(free_orgs)
        }
        
        # Add helpful information
        if organization_names:
            response["note"] = f"Organization names: {', '.join(organization_names[:5])}{'...' if len(organization_names) > 5 else ''}"
        else:
            response["note"] = f"No organizations found matching filter '{filter}' for this member"
        
        # Add organization details based on filter
        if filter == "public" or filter == "all":
            if public_orgs:
                response["public_orgs"] = public_orgs
                response["public_org_names"] = [org.get("name") for org in public_orgs]
        
        if filter == "private" or filter == "all":
            if private_orgs:
                response["private_orgs"] = private_orgs
                response["private_org_names"] = [org.get("name") for org in private_orgs]
        
        if filter == "paid" or filter == "all":
            if paid_orgs:
                response["paid_orgs"] = paid_orgs
                response["paid_org_names"] = [org.get("name") for org in paid_orgs]
        
        if filter == "free" or filter == "all":
            if free_orgs:
                response["free_orgs"] = free_orgs
                response["free_org_names"] = [org.get("name") for org in free_orgs]
        
        # Add filter analysis
        response["filter_analysis"] = {
            "applied_filter": filter,
            "total_matching": organizations_count,
            "public_matching": len(public_orgs),
            "private_matching": len(private_orgs),
            "paid_matching": len(paid_orgs),
            "free_matching": len(free_orgs),
            "filter_effectiveness": f"Filter '{filter}' returned {organizations_count} organizations"
        }
        
        # Add organization summary
        response["organization_summary"] = {
            "total": organizations_count,
            "public": len(public_orgs),
            "private": len(private_orgs),
            "paid": len(paid_orgs),
            "free": len(free_orgs)
        }
        
        return response
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve member organizations: {str(e)}",
            "action": "get_member_organizations_filtered",
            "member_id": id_member,
            "filter": filter,
            "message": f"Failed to retrieve organizations with filter '{filter}' for member {id_member}"
        }


@mcp.tool(
    "TRELLO_GET_MEMBERS_ORGANIZATIONS_INVITED_BY_ID_MEMBER",
    description="Retrieve member's invited organizations. Retrieves organizations a trello member has been invited to but has not yet accepted or declined.",
)
def TRELLO_GET_MEMBERS_ORGANIZATIONS_INVITED_BY_ID_MEMBER(
    id_member: Annotated[str, "The ID or username of the member to get invited organizations for."],
    fields: Annotated[str, "The fields to retrieve from the invited organizations (e.g., id, name, displayName, desc, descData, url, website, logoHash, products, powerUps, prefs, billableMemberCount, invitations, invited, limits, memberships, premiumFeatures). Defaults to all."] = "all"
):
    """Retrieve member's invited organizations. Retrieves organizations a trello member has been invited to but has not yet accepted or declined."""
    err = _validate_required({"id_member": id_member}, ["id_member"])
    if err:
        return err
    
    try:
        # Get invited organizations for the member
        endpoint = f"/members/{id_member}/organizationsInvited"
        
        # Build query parameters
        params = {}
        if fields is not None:
            params["fields"] = fields
        
        # Make the API request
        result = trello_request("GET", endpoint, params=params)
        
        if not isinstance(result, list):
            return {
                "successful": False,
                "error": "Invalid invited organizations data received",
                "action": "get_member_organizations_invited",
                "member_id": id_member,
                "message": f"Failed to retrieve invited organizations for member {id_member}"
            }
        
        # Extract key information
        invited_organizations_count = len(result)
        organization_ids = [org.get("id") for org in result if org.get("id")]
        organization_names = [org.get("name") for org in result if org.get("name")]
        organization_display_names = [org.get("displayName") for org in result if org.get("displayName")]
        
        # Analyze organization types
        public_orgs = [org for org in result if org.get("prefs", {}).get("permissionLevel") == "public"]
        private_orgs = [org for org in result if org.get("prefs", {}).get("permissionLevel") == "private"]
        paid_orgs = [org for org in result if org.get("paid_account", False)]
        free_orgs = [org for org in result if not org.get("paid_account", False)]
        
        response = {
            "successful": True,
            "data": result,
            "action": "get_member_organizations_invited",
            "member_id": id_member,
            "invited_organizations_count": invited_organizations_count,
            "organization_ids": organization_ids,
            "organization_names": organization_names,
            "organization_display_names": organization_display_names,
            "message": f"Successfully retrieved {invited_organizations_count} invited organizations for member {id_member}",
            "invited_organizations": result
        }
        
        # Add organization analysis
        response["organization_analysis"] = {
            "total_invited_organizations": invited_organizations_count,
            "public_invited_organizations": len(public_orgs),
            "private_invited_organizations": len(private_orgs),
            "paid_invited_organizations": len(paid_orgs),
            "free_invited_organizations": len(free_orgs)
        }
        
        # Add helpful information
        if organization_names:
            response["note"] = f"Invited organization names: {', '.join(organization_names[:5])}{'...' if len(organization_names) > 5 else ''}"
        else:
            response["note"] = "No pending organization invitations found for this member"
        
        # Add organization details
        if public_orgs:
            response["public_invited_orgs"] = public_orgs
            response["public_invited_org_names"] = [org.get("name") for org in public_orgs]
        
        if private_orgs:
            response["private_invited_orgs"] = private_orgs
            response["private_invited_org_names"] = [org.get("name") for org in private_orgs]
        
        if paid_orgs:
            response["paid_invited_orgs"] = paid_orgs
            response["paid_invited_org_names"] = [org.get("name") for org in paid_orgs]
        
        if free_orgs:
            response["free_invited_orgs"] = free_orgs
            response["free_invited_org_names"] = [org.get("name") for org in free_orgs]
        
        # Add invitation summary
        response["invitation_summary"] = {
            "total_pending": invited_organizations_count,
            "public_pending": len(public_orgs),
            "private_pending": len(private_orgs),
            "paid_pending": len(paid_orgs),
            "free_pending": len(free_orgs)
        }
        
        # Add invitation status information
        response["invitation_status"] = {
            "status": "pending",
            "description": "These organizations have invited the member but the invitation has not been accepted or declined",
            "action_required": "Member needs to accept or decline these invitations",
            "total_pending": invited_organizations_count
        }
        
        # Add helpful information for managing invitations
        if invited_organizations_count > 0:
            response["invitation_management"] = {
                "note": f"Member has {invited_organizations_count} pending organization invitations",
                "next_steps": "Use Trello web interface or API to accept/decline invitations",
                "organizations_awaiting_response": organization_names
            }
        else:
            response["invitation_management"] = {
                "note": "No pending organization invitations",
                "status": "All invitations have been processed or no invitations exist"
            }
        
        return response
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve member invited organizations: {str(e)}",
            "action": "get_member_organizations_invited",
            "member_id": id_member,
            "message": f"Failed to retrieve invited organizations for member {id_member}"
        }


@mcp.tool(
    "TRELLO_GET_MEMBERS_ORGANIZATIONS_INVITED_BY_ID_MEMBER_BY_FIELD",
    description="Get field of member's invited organization. Get a specific field of an organization to which the member has a pending invitation; returns data only if such an invitation exists.",
)
def TRELLO_GET_MEMBERS_ORGANIZATIONS_INVITED_BY_ID_MEMBER_BY_FIELD(
    id_member: Annotated[str, "The ID or username of the member to get invited organization field for."],
    field: Annotated[str, "The specific field to retrieve from the invited organization (e.g., id, name, displayName, desc, url, website, logoHash, prefs, paid_account, billableMemberCount, premiumFeatures)."]
):
    """Get field of member's invited organization. Get a specific field of an organization to which the member has a pending invitation; returns data only if such an invitation exists."""
    err = _validate_required({"id_member": id_member, "field": field}, ["id_member", "field"])
    if err:
        return err
    
    try:
        # Get invited organizations for the member with specific field
        endpoint = f"/members/{id_member}/organizationsInvited"
        
        # Build query parameters
        params = {
            "fields": field
        }
        
        # Make the API request
        result = trello_request("GET", endpoint, params=params)
        
        if not isinstance(result, list):
            return {
                "successful": False,
                "error": "Invalid invited organizations data received",
                "action": "get_member_organizations_invited_field",
                "member_id": id_member,
                "field": field,
                "message": f"Failed to retrieve invited organization field '{field}' for member {id_member}"
            }
        
        # Extract key information
        invited_organizations_count = len(result)
        
        # Extract the specific field values
        field_values = []
        for org in result:
            if field in org:
                field_values.append(org[field])
            else:
                field_values.append(None)
        
        # Filter out None values for cleaner response
        valid_field_values = [value for value in field_values if value is not None]
        
        response = {
            "successful": True,
            "data": result,
            "action": "get_member_organizations_invited_field",
            "member_id": id_member,
            "field": field,
            "invited_organizations_count": invited_organizations_count,
            "field_values": field_values,
            "valid_field_values": valid_field_values,
            "field_values_count": len(valid_field_values),
            "message": f"Successfully retrieved field '{field}' from {invited_organizations_count} invited organizations for member {id_member}",
            "invited_organizations": result
        }
        
        # Add field-specific information
        if field == "id":
            response["note"] = "Organization IDs from pending invitations"
            response["field_description"] = "Unique identifiers of organizations that have invited the member"
        elif field == "name":
            response["note"] = "Organization names from pending invitations"
            response["field_description"] = "Names of organizations that have invited the member"
        elif field == "displayName":
            response["note"] = "Organization display names from pending invitations"
            response["field_description"] = "Display names of organizations that have invited the member"
        elif field == "desc":
            response["note"] = "Organization descriptions from pending invitations"
            response["field_description"] = "Descriptions of organizations that have invited the member"
        elif field == "url":
            response["note"] = "Organization URLs from pending invitations"
            response["field_description"] = "URLs of organizations that have invited the member"
        elif field == "website":
            response["note"] = "Organization websites from pending invitations"
            response["field_description"] = "Website URLs of organizations that have invited the member"
        elif field == "logoHash":
            response["note"] = "Organization logo hashes from pending invitations"
            response["field_description"] = "Logo hashes of organizations that have invited the member"
        elif field == "prefs":
            response["note"] = "Organization preferences from pending invitations"
            response["field_description"] = "Preferences of organizations that have invited the member"
        elif field == "paid_account":
            response["note"] = "Organization paid account status from pending invitations"
            response["field_description"] = "Whether organizations that have invited the member have paid accounts"
        elif field == "billableMemberCount":
            response["note"] = "Organization billable member counts from pending invitations"
            response["field_description"] = "Number of billable members in organizations that have invited the member"
        elif field == "premiumFeatures":
            response["note"] = "Organization premium features from pending invitations"
            response["field_description"] = "Premium features available in organizations that have invited the member"
        else:
            response["note"] = f"Field '{field}' values from pending invitations"
            response["field_description"] = f"Values of field '{field}' from organizations that have invited the member"
        
        # Add helpful information
        if valid_field_values:
            if len(valid_field_values) <= 5:
                response["note"] = f"Field '{field}' values: {', '.join(map(str, valid_field_values))}"
            else:
                response["note"] = f"Field '{field}' values: {', '.join(map(str, valid_field_values[:5]))}... (and {len(valid_field_values) - 5} more)"
        else:
            response["note"] = f"No valid values found for field '{field}' in pending invitations"
        
        # Add field analysis
        response["field_analysis"] = {
            "requested_field": field,
            "total_organizations": invited_organizations_count,
            "organizations_with_field": len(valid_field_values),
            "organizations_without_field": invited_organizations_count - len(valid_field_values),
            "field_coverage": f"{len(valid_field_values)}/{invited_organizations_count} organizations have this field"
        }
        
        # Add invitation status
        response["invitation_status"] = {
            "status": "pending",
            "description": "These are organizations with pending invitations",
            "field_availability": f"Field '{field}' is available in {len(valid_field_values)} out of {invited_organizations_count} organizations"
        }
        
        return response
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve member invited organization field: {str(e)}",
            "action": "get_member_organizations_invited_field",
            "member_id": id_member,
            "field": field,
            "message": f"Failed to retrieve invited organization field '{field}' for member {id_member}"
        }


@mcp.tool(
    "TRELLO_GET_MEMBERS_TOKENS_BY_ID_MEMBER",
    description="Retrieve member tokens. Gets api token metadata for a trello member; actual token values are excluded for security.",
)
def TRELLO_GET_MEMBERS_TOKENS_BY_ID_MEMBER(
    id_member: Annotated[str, "The ID or username of the member to get tokens for."],
    filter: Annotated[str, "The filter criteria for tokens (e.g., 'all', 'active', 'expired'). Defaults to all."] = "all"
):
    """Retrieve member tokens. Gets api token metadata for a trello member; actual token values are excluded for security."""
    err = _validate_required({"id_member": id_member}, ["id_member"])
    if err:
        return err
    
    try:
        # Get tokens for the member
        endpoint = f"/members/{id_member}/tokens"
        
        # Build query parameters
        params = {}
        if filter is not None:
            params["filter"] = filter
        
        # Make the API request
        result = trello_request("GET", endpoint, params=params)
        
        if not isinstance(result, list):
            return {
                "successful": False,
                "error": "Invalid tokens data received",
                "action": "get_member_tokens",
                "member_id": id_member,
                "message": f"Failed to retrieve tokens for member {id_member}"
            }
        
        # Extract key information
        tokens_count = len(result)
        token_ids = [token.get("id") for token in result if token.get("id")]
        token_identifiers = [token.get("identifier") for token in result if token.get("identifier")]
        token_permissions = [token.get("permissions") for token in result if token.get("permissions")]
        
        # Analyze token status
        active_tokens = [token for token in result if token.get("dateExpires") is None or token.get("dateExpires") == ""]
        expired_tokens = [token for token in result if token.get("dateExpires") is not None and token.get("dateExpires") != ""]
        
        # Analyze token permissions
        read_tokens = [token for token in result if token.get("permissions") == "read"]
        write_tokens = [token for token in result if token.get("permissions") == "write"]
        admin_tokens = [token for token in result if token.get("permissions") == "admin"]
        
        response = {
            "successful": True,
            "data": result,
            "action": "get_member_tokens",
            "member_id": id_member,
            "tokens_count": tokens_count,
            "token_ids": token_ids,
            "token_identifiers": token_identifiers,
            "token_permissions": token_permissions,
            "message": f"Successfully retrieved {tokens_count} tokens for member {id_member}",
            "tokens": result
        }
        
        # Add token analysis
        response["token_analysis"] = {
            "total_tokens": tokens_count,
            "active_tokens": len(active_tokens),
            "expired_tokens": len(expired_tokens),
            "read_tokens": len(read_tokens),
            "write_tokens": len(write_tokens),
            "admin_tokens": len(admin_tokens)
        }
        
        # Add filter information
        if filter != "all":
            response["filter_applied"] = filter
            response["filter_description"] = f"Tokens filtered by: {filter}"
        
        # Add helpful information
        if token_identifiers:
            response["note"] = f"Token identifiers: {', '.join(token_identifiers[:5])}{'...' if len(token_identifiers) > 5 else ''}"
        else:
            response["note"] = "No tokens found for this member"
        
        # Add token details
        if active_tokens:
            response["active_tokens"] = active_tokens
            response["active_token_ids"] = [token.get("id") for token in active_tokens]
        
        if expired_tokens:
            response["expired_tokens"] = expired_tokens
            response["expired_token_ids"] = [token.get("id") for token in expired_tokens]
        
        if read_tokens:
            response["read_tokens"] = read_tokens
            response["read_token_ids"] = [token.get("id") for token in read_tokens]
        
        if write_tokens:
            response["write_tokens"] = write_tokens
            response["write_token_ids"] = [token.get("id") for token in write_tokens]
        
        if admin_tokens:
            response["admin_tokens"] = admin_tokens
            response["admin_token_ids"] = [token.get("id") for token in admin_tokens]
        
        # Add security information
        response["security_info"] = {
            "note": "Actual token values are excluded for security reasons",
            "data_included": "Token metadata only (ID, identifier, permissions, dates)",
            "data_excluded": "Actual token values, secrets, and sensitive data",
            "purpose": "Token management and monitoring without exposing credentials"
        }
        
        # Add token summary
        response["token_summary"] = {
            "total": tokens_count,
            "active": len(active_tokens),
            "expired": len(expired_tokens),
            "read": len(read_tokens),
            "write": len(write_tokens),
            "admin": len(admin_tokens)
        }
        
        # Add token management information
        if tokens_count > 0:
            response["token_management"] = {
                "note": f"Member has {tokens_count} API tokens",
                "active_tokens": len(active_tokens),
                "expired_tokens": len(expired_tokens),
                "permission_breakdown": {
                    "read": len(read_tokens),
                    "write": len(write_tokens),
                    "admin": len(admin_tokens)
                }
            }
        else:
            response["token_management"] = {
                "note": "No API tokens found for this member",
                "status": "Member has not created any API tokens"
            }
        
        return response
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve member tokens: {str(e)}",
            "action": "get_member_tokens",
            "member_id": id_member,
            "message": f"Failed to retrieve tokens for member {id_member}"
        }


@mcp.tool(
    "TRELLO_GET_TOKENS_BY_TOKEN",
    description="Get token by token. Retrieves information about a specific trello api token, allowing selection of specific fields and inclusion of webhook details.",
)
def TRELLO_GET_TOKENS_BY_TOKEN(
    token: Annotated[str, "The API token to retrieve information for."],
    fields: Annotated[str, "Specific fields to retrieve. Defaults to all fields."] = "all",
    webhooks: Annotated[str, "Whether to include webhook details. Set to 'true' to include webhooks."] = "false"
):
    """Get token by token. Retrieves information about a specific trello api token, allowing selection of specific fields and inclusion of webhook details."""
    err = _validate_required({"token": token}, ["token"])
    if err:
        return err
    
    try:
        # Get token information
        endpoint = f"/tokens/{token}"
        
        # Build query parameters
        params = {}
        if fields != "all":
            params["fields"] = fields
        if webhooks.lower() == "true":
            params["webhooks"] = "true"
        
        # Make the API request
        result = trello_request("GET", endpoint, params=params)
        
        if not isinstance(result, dict):
            return {
                "successful": False,
                "error": "Invalid token data received",
                "action": "get_token_by_token",
                "token": token,
                "message": f"Failed to retrieve information for token {token}"
            }
        
        # Extract key information
        token_id = result.get("id")
        token_identifier = result.get("identifier")
        token_permissions = result.get("permissions")
        token_date_created = result.get("dateCreated")
        token_date_expires = result.get("dateExpires")
        token_member_id = result.get("idMember")
        token_webhooks = result.get("webhooks", [])
        
        # Analyze token status
        is_active = token_date_expires is None or token_date_expires == ""
        is_expired = token_date_expires is not None and token_date_expires != ""
        
        response = {
            "successful": True,
            "data": result,
            "action": "get_token_by_token",
            "token": token,
            "token_id": token_id,
            "token_identifier": token_identifier,
            "token_permissions": token_permissions,
            "token_date_created": token_date_created,
            "token_date_expires": token_date_expires,
            "token_member_id": token_member_id,
            "message": f"Successfully retrieved information for token {token}"
        }
        
        # Add token status information
        response["token_status"] = {
            "is_active": is_active,
            "is_expired": is_expired,
            "status": "active" if is_active else "expired"
        }
        
        # Add webhook information if requested
        if webhooks.lower() == "true":
            response["webhooks"] = token_webhooks
            response["webhooks_count"] = len(token_webhooks)
            response["webhook_ids"] = [webhook.get("id") for webhook in token_webhooks if webhook.get("id")]
        else:
            response["webhooks_included"] = False
            response["note"] = "Webhook details not included. Set webhooks parameter to 'true' to include webhook information."
        
        # Add field information
        if fields != "all":
            response["fields_requested"] = fields
            response["fields_description"] = f"Only requested fields included: {fields}"
        else:
            response["fields_requested"] = "all"
            response["fields_description"] = "All available fields included"
        
        # Add token analysis
        response["token_analysis"] = {
            "permissions": token_permissions,
            "created": token_date_created,
            "expires": token_date_expires,
            "member_id": token_member_id,
            "identifier": token_identifier
        }
        
        # Add security information
        response["security_info"] = {
            "note": "Token information retrieved successfully",
            "data_included": "Token metadata and configuration",
            "webhooks_included": webhooks.lower() == "true",
            "fields_included": fields
        }
        
        # Add helpful information
        if token_identifier:
            response["note"] = f"Token identifier: {token_identifier}"
        else:
            response["note"] = "Token information retrieved (no identifier available)"
        
        # Add webhook details if included
        if webhooks.lower() == "true" and token_webhooks:
            response["webhook_details"] = {
                "count": len(token_webhooks),
                "webhooks": token_webhooks,
                "active_webhooks": [w for w in token_webhooks if w.get("active", True)],
                "inactive_webhooks": [w for w in token_webhooks if not w.get("active", True)]
            }
        
        return response
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve token information: {str(e)}",
            "action": "get_token_by_token",
            "token": token,
            "message": f"Failed to retrieve information for token {token}"
        }


@mcp.tool(
    "TRELLO_GET_TOKENS_BY_TOKEN_BY_FIELD",
    description="Get token field. Retrieves a specific field from a trello token, provided the token is valid, has necessary permissions, and the field is a valid token field.",
)
def TRELLO_GET_TOKENS_BY_TOKEN_BY_FIELD(
    token: Annotated[str, "The API token to retrieve the field from."],
    field: Annotated[str, "The specific field to retrieve from the token (e.g., id, identifier, permissions, dateCreated, dateExpires, idMember, webhooks)."]
):
    """Get token field. Retrieves a specific field from a trello token, provided the token is valid, has necessary permissions, and the field is a valid token field."""
    err = _validate_required({"token": token, "field": field}, ["token", "field"])
    if err:
        return err
    
    try:
        # Get token information first
        endpoint = f"/tokens/{token}"
        
        # Make the API request
        result = trello_request("GET", endpoint)
        
        if not isinstance(result, dict):
            return {
                "successful": False,
                "error": "Invalid token data received",
                "action": "get_token_field",
                "token": token,
                "field": field,
                "message": f"Failed to retrieve token information for field '{field}'"
            }
        
        # Check if the requested field exists
        if field not in result:
            available_fields = list(result.keys())
            return {
                "successful": False,
                "error": f"Field '{field}' not found in token data",
                "action": "get_token_field",
                "token": token,
                "field": field,
                "available_fields": available_fields,
                "message": f"Field '{field}' is not available. Available fields: {', '.join(available_fields)}"
            }
        
        # Get the field value
        field_value = result.get(field)
        
        # Extract additional context for better response
        token_id = result.get("id")
        token_identifier = result.get("identifier")
        token_permissions = result.get("permissions")
        
        response = {
            "successful": True,
            "data": {
                "field": field,
                "value": field_value,
                "token_id": token_id,
                "token_identifier": token_identifier
            },
            "action": "get_token_field",
            "token": token,
            "field": field,
            "field_value": field_value,
            "message": f"Successfully retrieved field '{field}' from token {token}"
        }
        
        # Add field-specific information
        response["field_info"] = {
            "field_name": field,
            "field_value": field_value,
            "field_type": type(field_value).__name__,
            "is_empty": field_value is None or field_value == "",
            "is_list": isinstance(field_value, list),
            "is_dict": isinstance(field_value, dict)
        }
        
        # Add token context
        response["token_context"] = {
            "token_id": token_id,
            "token_identifier": token_identifier,
            "token_permissions": token_permissions,
            "field_source": "Trello API token data"
        }
        
        # Add helpful information based on field type
        if isinstance(field_value, list):
            response["field_analysis"] = {
                "type": "list",
                "count": len(field_value),
                "items": field_value[:5] if len(field_value) > 5 else field_value,
                "truncated": len(field_value) > 5
            }
        elif isinstance(field_value, dict):
            response["field_analysis"] = {
                "type": "dictionary",
                "keys": list(field_value.keys()),
                "key_count": len(field_value.keys())
            }
        elif isinstance(field_value, str):
            response["field_analysis"] = {
                "type": "string",
                "length": len(field_value),
                "is_empty": field_value == "",
                "is_date": "date" in field.lower() and field_value != ""
            }
        else:
            response["field_analysis"] = {
                "type": type(field_value).__name__,
                "value": field_value
            }
        
        # Add validation information
        response["validation"] = {
            "token_valid": True,
            "field_exists": True,
            "field_accessible": True,
            "permissions_sufficient": True
        }
        
        # Add security information
        response["security_info"] = {
            "note": f"Field '{field}' retrieved from token data",
            "data_type": "Token field value",
            "sensitivity": "Token metadata (no sensitive credentials exposed)"
        }
        
        return response
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve token field: {str(e)}",
            "action": "get_token_field",
            "token": token,
            "field": field,
            "message": f"Failed to retrieve field '{field}' from token {token}"
        }


@mcp.tool(
    "TRELLO_GET_TOKENS_MEMBER_BY_TOKEN",
    description="Get token member. Retrieves information about the trello member associated with the current api token, allowing customization of the returned fields.",
)
def TRELLO_GET_TOKENS_MEMBER_BY_TOKEN(
    fields: Annotated[str, "Specific fields to retrieve from the member. Defaults to all fields."] = "all"
):
    """Get token member. Retrieves information about the trello member associated with the current api token, allowing customization of the returned fields."""
    try:
        # Get member information associated with the current token
        endpoint = "/members/me"
        
        # Build query parameters
        params = {}
        if fields != "all":
            params["fields"] = fields
        
        # Make the API request
        result = trello_request("GET", endpoint, params=params)
        
        if not isinstance(result, dict):
            return {
                "successful": False,
                "error": "Invalid member data received",
                "action": "get_token_member",
                "message": "Failed to retrieve member information for current token"
            }
        
        # Extract key information
        member_id = result.get("id")
        member_username = result.get("username")
        member_full_name = result.get("fullName")
        member_email = result.get("email")
        member_avatar_hash = result.get("avatarHash")
        member_bio = result.get("bio")
        member_member_type = result.get("memberType")
        member_url = result.get("url")
        member_prefs = result.get("prefs", {})
        member_id_boards = result.get("idBoards", [])
        member_id_organizations = result.get("idOrganizations", [])
        member_confirmed = result.get("confirmed")
        member_premium_features = result.get("premiumFeatures", [])
        
        response = {
            "successful": True,
            "data": result,
            "action": "get_token_member",
            "member_id": member_id,
            "member_username": member_username,
            "member_full_name": member_full_name,
            "message": f"Successfully retrieved member information for current token"
        }
        
        # Add member summary
        response["member_summary"] = {
            "id": member_id,
            "username": member_username,
            "full_name": member_full_name,
            "email": member_email,
            "member_type": member_member_type,
            "confirmed": member_confirmed,
            "url": member_url
        }
        
        # Add member statistics
        response["member_stats"] = {
            "boards_count": len(member_id_boards) if member_id_boards else 0,
            "organizations_count": len(member_id_organizations) if member_id_organizations else 0,
            "premium_features_count": len(member_premium_features) if member_premium_features else 0,
            "has_avatar": member_avatar_hash is not None and member_avatar_hash != "",
            "has_bio": member_bio is not None and member_bio != ""
        }
        
        # Add field information
        if fields != "all":
            response["fields_requested"] = fields
            response["fields_description"] = f"Only requested fields included: {fields}"
        else:
            response["fields_requested"] = "all"
            response["fields_description"] = "All available member fields included"
        
        # Add member preferences analysis
        if member_prefs:
            response["member_preferences"] = {
                "preferences_available": True,
                "preference_keys": list(member_prefs.keys()),
                "preference_count": len(member_prefs)
            }
        else:
            response["member_preferences"] = {
                "preferences_available": False,
                "note": "No member preferences available"
            }
        
        # Add board and organization information
        if member_id_boards:
            response["boards_info"] = {
                "count": len(member_id_boards),
                "board_ids": member_id_boards[:10],  # Show first 10
                "truncated": len(member_id_boards) > 10
            }
        
        if member_id_organizations:
            response["organizations_info"] = {
                "count": len(member_id_organizations),
                "organization_ids": member_id_organizations[:10],  # Show first 10
                "truncated": len(member_id_organizations) > 10
            }
        
        # Add premium features information
        if member_premium_features:
            response["premium_features"] = {
                "count": len(member_premium_features),
                "features": member_premium_features,
                "is_premium": True
            }
        else:
            response["premium_features"] = {
                "count": 0,
                "features": [],
                "is_premium": False
            }
        
        # Add member profile analysis
        response["profile_analysis"] = {
            "completeness": {
                "has_username": member_username is not None and member_username != "",
                "has_full_name": member_full_name is not None and member_full_name != "",
                "has_email": member_email is not None and member_email != "",
                "has_avatar": member_avatar_hash is not None and member_avatar_hash != "",
                "has_bio": member_bio is not None and member_bio != ""
            },
            "activity": {
                "boards_count": len(member_id_boards) if member_id_boards else 0,
                "organizations_count": len(member_id_organizations) if member_id_organizations else 0,
                "is_active": len(member_id_boards) > 0 or len(member_id_organizations) > 0
            }
        }
        
        # Add security information
        response["security_info"] = {
            "note": "Member information retrieved for current token",
            "data_type": "Member profile and activity data",
            "sensitivity": "Public member information (no sensitive credentials)",
            "token_associated": True
        }
        
        # Add helpful information
        if member_username:
            response["note"] = f"Member: {member_username} ({member_full_name or 'No full name'})"
        else:
            response["note"] = f"Member ID: {member_id}"
        
        return response
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve member information: {str(e)}",
            "action": "get_token_member",
            "message": "Failed to retrieve member information for current token"
        }


@mcp.tool(
    "TRELLO_TOKEN_GET_MEMBER_BY_TOKEN",
    description="Get token member. Retrieves information for the trello member associated with the api token, with customizable fields. <<deprecated: please use the 'get tokens member by token' action instead.>>",
)
def TRELLO_TOKEN_GET_MEMBER_BY_TOKEN(
    fields: Annotated[str, "Specific fields to retrieve from the member. Defaults to all fields."] = "all"
):
    """Get token member. Retrieves information for the trello member associated with the api token, with customizable fields. <<deprecated: please use the 'get tokens member by token' action instead.>>"""
    # This is a deprecated wrapper around TRELLO_GET_TOKENS_MEMBER_BY_TOKEN
    return TRELLO_GET_TOKENS_MEMBER_BY_TOKEN(
        fields=fields
    )


@mcp.tool(
    "TRELLO_GET_TOKENS_MEMBER_BY_TOKEN_BY_FIELD",
    description="Retrieve token member field. Retrieves a specific field for the trello member associated with the provided api token.",
)
def TRELLO_GET_TOKENS_MEMBER_BY_TOKEN_BY_FIELD(
    field: Annotated[str, "The specific field to retrieve from the member associated with the current token (e.g., id, username, fullName, initials, avatarHash, email, bio, bioData, confirmed, memberType, url, gravatarHash, uploadedAvatarHash, prefs, trophies, uploadedAvatarId, premiumFeatures, idBoards, idOrganizations, loginTypes, newEmail, oneTimeMessagesDismissed, marketingOptIn, messagesDismissed, tags, savedSearches, idEnterprisesAdmin, idEnterprisesDeactivated, limits, marketingOptInDate, idPremOrgsAdmin, avatarSource, emailUnread)."]
):
    """Retrieve token member field. Retrieves a specific field for the trello member associated with the provided api token."""
    err = _validate_required({"field": field}, ["field"])
    if err:
        return err
    
    try:
        # Get member information associated with the current token
        endpoint = "/members/me"
        
        # Make the API request
        result = trello_request("GET", endpoint)
        
        if not isinstance(result, dict):
            return {
                "successful": False,
                "error": "Invalid member data received",
                "action": "get_token_member_field",
                "field": field,
                "message": f"Failed to retrieve member information for field '{field}'"
            }
        
        # Check if the requested field exists
        if field not in result:
            available_fields = list(result.keys())
            return {
                "successful": False,
                "error": f"Field '{field}' not found in member data",
                "action": "get_token_member_field",
                "field": field,
                "available_fields": available_fields,
                "message": f"Field '{field}' is not available. Available fields: {', '.join(available_fields)}"
            }
        
        # Get the field value
        field_value = result.get(field)
        
        # Extract additional context for better response
        member_id = result.get("id")
        member_username = result.get("username")
        member_full_name = result.get("fullName")
        
        response = {
            "successful": True,
            "data": {
                "field": field,
                "value": field_value,
                "member_id": member_id,
                "member_username": member_username
            },
            "action": "get_token_member_field",
            "field": field,
            "field_value": field_value,
            "message": f"Successfully retrieved field '{field}' from member associated with current token"
        }
        
        # Add field-specific information
        response["field_info"] = {
            "field_name": field,
            "field_value": field_value,
            "field_type": type(field_value).__name__,
            "is_empty": field_value is None or field_value == "",
            "is_list": isinstance(field_value, list),
            "is_dict": isinstance(field_value, dict)
        }
        
        # Add member context
        response["member_context"] = {
            "member_id": member_id,
            "member_username": member_username,
            "member_full_name": member_full_name,
            "field_source": "Trello member data for current token"
        }
        
        # Add helpful information based on field type
        if isinstance(field_value, list):
            response["field_analysis"] = {
                "type": "list",
                "count": len(field_value),
                "items": field_value[:5] if len(field_value) > 5 else field_value,
                "truncated": len(field_value) > 5
            }
        elif isinstance(field_value, dict):
            response["field_analysis"] = {
                "type": "dictionary",
                "keys": list(field_value.keys()),
                "key_count": len(field_value.keys())
            }
        elif isinstance(field_value, str):
            response["field_analysis"] = {
                "type": "string",
                "length": len(field_value),
                "is_empty": field_value == "",
                "is_date": "date" in field.lower() and field_value != "",
                "is_url": field.lower() in ["url", "avatarurl", "gravatarurl"] and field_value != ""
            }
        else:
            response["field_analysis"] = {
                "type": type(field_value).__name__,
                "value": field_value
            }
        
        # Add field-specific context based on common member fields
        if field == "idBoards":
            response["field_context"] = {
                "description": "List of board IDs the member has access to",
                "count": len(field_value) if isinstance(field_value, list) else 0,
                "is_activity_indicator": True
            }
        elif field == "idOrganizations":
            response["field_context"] = {
                "description": "List of organization IDs the member belongs to",
                "count": len(field_value) if isinstance(field_value, list) else 0,
                "is_activity_indicator": True
            }
        elif field == "premiumFeatures":
            response["field_context"] = {
                "description": "List of premium features available to the member",
                "count": len(field_value) if isinstance(field_value, list) else 0,
                "is_premium_indicator": True
            }
        elif field == "prefs":
            response["field_context"] = {
                "description": "Member preferences and settings",
                "is_preferences": True,
                "key_count": len(field_value) if isinstance(field_value, dict) else 0
            }
        elif field in ["username", "fullName", "email"]:
            response["field_context"] = {
                "description": f"Member {field} information",
                "is_profile_field": True,
                "is_identifying": True
            }
        elif field in ["avatarHash", "gravatarHash", "uploadedAvatarHash"]:
            response["field_context"] = {
                "description": f"Member avatar {field}",
                "is_avatar_field": True,
                "has_avatar": field_value is not None and field_value != ""
            }
        
        # Add validation information
        response["validation"] = {
            "token_valid": True,
            "member_accessible": True,
            "field_exists": True,
            "field_accessible": True,
            "permissions_sufficient": True
        }
        
        # Add security information
        response["security_info"] = {
            "note": f"Field '{field}' retrieved from member data for current token",
            "data_type": "Member field value",
            "sensitivity": "Public member information (no sensitive credentials exposed)",
            "token_associated": True
        }
        
        # Add helpful information
        if member_username:
            response["note"] = f"Field '{field}' for member: {member_username}"
        else:
            response["note"] = f"Field '{field}' for member ID: {member_id}"
        
        return response
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve member field: {str(e)}",
            "action": "get_token_member_field",
            "field": field,
            "message": f"Failed to retrieve field '{field}' from member associated with current token"
        }


@mcp.tool(
    "TRELLO_GET_TOKENS_WEBHOOKS_BY_TOKEN",
    description="Get webhooks for token. Retrieves all webhooks associated with a specific trello api token.",
)
def TRELLO_GET_TOKENS_WEBHOOKS_BY_TOKEN(
    token: Annotated[str, "The API token to retrieve webhooks for."]
):
    """Get webhooks for token. Retrieves all webhooks associated with a specific trello api token."""
    err = _validate_required({"token": token}, ["token"])
    if err:
        return err
    
    try:
        # Get token information with webhooks included
        endpoint = f"/tokens/{token}"
        
        # Build query parameters to include webhooks
        params = {
            "webhooks": "true"
        }
        
        # Make the API request
        result = trello_request("GET", endpoint, params=params)
        
        if not isinstance(result, dict):
            return {
                "successful": False,
                "error": "Invalid token data received",
                "action": "get_token_webhooks",
                "message": f"Failed to retrieve token information for webhooks"
            }
        
        # Extract webhooks from token data
        webhooks = result.get("webhooks", [])
        
        if not isinstance(webhooks, list):
            return {
                "successful": False,
                "error": "Invalid webhooks data in token response",
                "action": "get_token_webhooks",
                "message": f"Failed to extract webhooks from token data"
            }
        
        # Extract key information
        webhooks_count = len(webhooks)
        webhook_ids = [webhook.get("id") for webhook in webhooks if webhook.get("id")]
        webhook_urls = [webhook.get("callbackURL") for webhook in webhooks if webhook.get("callbackURL")]
        webhook_models = [webhook.get("idModel") for webhook in webhooks if webhook.get("idModel")]
        webhook_descriptions = [webhook.get("description") for webhook in webhooks if webhook.get("description")]
        
        # Analyze webhook status
        active_webhooks = [webhook for webhook in webhooks if webhook.get("active", True)]
        inactive_webhooks = [webhook for webhook in webhooks if not webhook.get("active", True)]
        
        # Analyze webhook types by model
        board_webhooks = [webhook for webhook in webhooks if webhook.get("idModel") and "board" in webhook.get("idModel", "")]
        card_webhooks = [webhook for webhook in webhooks if webhook.get("idModel") and "card" in webhook.get("idModel", "")]
        list_webhooks = [webhook for webhook in webhooks if webhook.get("idModel") and "list" in webhook.get("idModel", "")]
        organization_webhooks = [webhook for webhook in webhooks if webhook.get("idModel") and "organization" in webhook.get("idModel", "")]
        
        response = {
            "successful": True,
            "data": webhooks,
            "action": "get_token_webhooks",
            "webhooks_count": webhooks_count,
            "webhook_ids": webhook_ids,
            "webhook_urls": webhook_urls,
            "webhook_models": webhook_models,
            "webhook_descriptions": webhook_descriptions,
            "message": f"Successfully retrieved {webhooks_count} webhooks for token {token}"
        }
        
        # Add webhook analysis
        response["webhook_analysis"] = {
            "total_webhooks": webhooks_count,
            "active_webhooks": len(active_webhooks),
            "inactive_webhooks": len(inactive_webhooks),
            "board_webhooks": len(board_webhooks),
            "card_webhooks": len(card_webhooks),
            "list_webhooks": len(list_webhooks),
            "organization_webhooks": len(organization_webhooks)
        }
        
        # Add webhook status information
        response["webhook_status"] = {
            "active_count": len(active_webhooks),
            "inactive_count": len(inactive_webhooks),
            "status_breakdown": {
                "active": len(active_webhooks),
                "inactive": len(inactive_webhooks)
            }
        }
        
        # Add webhook type information
        response["webhook_types"] = {
            "board_webhooks": len(board_webhooks),
            "card_webhooks": len(card_webhooks),
            "list_webhooks": len(list_webhooks),
            "organization_webhooks": len(organization_webhooks),
            "other_webhooks": webhooks_count - len(board_webhooks) - len(card_webhooks) - len(list_webhooks) - len(organization_webhooks)
        }
        
        # Add detailed webhook information
        if active_webhooks:
            response["active_webhooks"] = active_webhooks
            response["active_webhook_ids"] = [webhook.get("id") for webhook in active_webhooks]
            response["active_webhook_urls"] = [webhook.get("callbackURL") for webhook in active_webhooks]
        
        if inactive_webhooks:
            response["inactive_webhooks"] = inactive_webhooks
            response["inactive_webhook_ids"] = [webhook.get("id") for webhook in inactive_webhooks]
            response["inactive_webhook_urls"] = [webhook.get("callbackURL") for webhook in inactive_webhooks]
        
        # Add webhook details by type
        if board_webhooks:
            response["board_webhooks"] = board_webhooks
            response["board_webhook_ids"] = [webhook.get("id") for webhook in board_webhooks]
        
        if card_webhooks:
            response["card_webhooks"] = card_webhooks
            response["card_webhook_ids"] = [webhook.get("id") for webhook in card_webhooks]
        
        if list_webhooks:
            response["list_webhooks"] = list_webhooks
            response["list_webhook_ids"] = [webhook.get("id") for webhook in list_webhooks]
        
        if organization_webhooks:
            response["organization_webhooks"] = organization_webhooks
            response["organization_webhook_ids"] = [webhook.get("id") for webhook in organization_webhooks]
        
        # Add webhook summary
        response["webhook_summary"] = {
            "total": webhooks_count,
            "active": len(active_webhooks),
            "inactive": len(inactive_webhooks),
            "by_type": {
                "boards": len(board_webhooks),
                "cards": len(card_webhooks),
                "lists": len(list_webhooks),
                "organizations": len(organization_webhooks)
            }
        }
        
        # Add webhook management information
        if webhooks_count > 0:
            response["webhook_management"] = {
                "note": f"Token has {webhooks_count} webhooks configured",
                "active_webhooks": len(active_webhooks),
                "inactive_webhooks": len(inactive_webhooks),
                "webhook_types": {
                    "boards": len(board_webhooks),
                    "cards": len(card_webhooks),
                    "lists": len(list_webhooks),
                    "organizations": len(organization_webhooks)
                }
            }
        else:
            response["webhook_management"] = {
                "note": "No webhooks configured for this token",
                "status": "Token has no webhooks set up"
            }
        
        # Add security information
        response["security_info"] = {
            "note": f"Webhook information retrieved for token {token}",
            "data_type": "Webhook configuration and status data",
            "sensitivity": "Webhook URLs and configuration (no sensitive credentials)",
            "token_associated": True
        }
        
        # Add helpful information
        if webhooks_count > 0:
            response["note"] = f"Found {webhooks_count} webhooks for token {token} ({len(active_webhooks)} active, {len(inactive_webhooks)} inactive)"
        else:
            response["note"] = f"No webhooks found for token {token}"
        
        return response
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve webhooks: {str(e)}",
            "action": "get_token_webhooks",
            "message": f"Failed to retrieve webhooks for token {token}"
        }


@mcp.tool(
    "TRELLO_GET_TOKENS_WEBHOOKS_BY_TOKEN_BY_ID_WEBHOOK",
    description="Get token webhook by ID. Retrieves detailed information for a specific trello webhook, identified by `idwebhook`, that is associated with the given `token`.",
)
def TRELLO_GET_TOKENS_WEBHOOKS_BY_TOKEN_BY_ID_WEBHOOK(
    idWebhook: Annotated[str, "The ID of the webhook to retrieve detailed information for."]
):
    """Get token webhook by ID. Retrieves detailed information for a specific trello webhook, identified by `idwebhook`, that is associated with the given `token`."""
    err = _validate_required({"idWebhook": idWebhook}, ["idWebhook"])
    if err:
        return err
    
    try:
        # Get webhook information by ID
        endpoint = f"/webhooks/{idWebhook}"
        
        # Make the API request
        result = trello_request("GET", endpoint)
        
        if not isinstance(result, dict):
            return {
                "successful": False,
                "error": "Invalid webhook data received",
                "action": "get_webhook_by_id",
                "webhook_id": idWebhook,
                "message": f"Failed to retrieve webhook {idWebhook}"
            }
        
        # Extract key information
        webhook_id = result.get("id")
        webhook_callback_url = result.get("callbackURL")
        webhook_id_model = result.get("idModel")
        webhook_description = result.get("description")
        webhook_active = result.get("active", True)
        webhook_consecutive_failures = result.get("consecutiveFailures", 0)
        webhook_first_consecutive_fail_date = result.get("firstConsecutiveFailDate")
        webhook_date_created = result.get("dateCreated")
        webhook_date_updated = result.get("dateUpdated")
        
        response = {
            "successful": True,
            "data": result,
            "action": "get_webhook_by_id",
            "webhook_id": webhook_id,
            "webhook_callback_url": webhook_callback_url,
            "webhook_id_model": webhook_id_model,
            "webhook_description": webhook_description,
            "webhook_active": webhook_active,
            "message": f"Successfully retrieved webhook {idWebhook}"
        }
        
        # Add webhook status information
        response["webhook_status"] = {
            "is_active": webhook_active,
            "status": "active" if webhook_active else "inactive",
            "consecutive_failures": webhook_consecutive_failures,
            "first_failure_date": webhook_first_consecutive_fail_date
        }
        
        # Add webhook configuration
        response["webhook_configuration"] = {
            "callback_url": webhook_callback_url,
            "model_id": webhook_id_model,
            "description": webhook_description,
            "created": webhook_date_created,
            "updated": webhook_date_updated
        }
        
        # Add webhook health information
        response["webhook_health"] = {
            "consecutive_failures": webhook_consecutive_failures,
            "is_healthy": webhook_consecutive_failures == 0,
            "first_failure_date": webhook_first_consecutive_fail_date,
            "health_status": "healthy" if webhook_consecutive_failures == 0 else "unhealthy"
        }
        
        # Add webhook model analysis
        if webhook_id_model:
            model_type = "unknown"
            if "board" in webhook_id_model.lower():
                model_type = "board"
            elif "card" in webhook_id_model.lower():
                model_type = "card"
            elif "list" in webhook_id_model.lower():
                model_type = "list"
            elif "organization" in webhook_id_model.lower():
                model_type = "organization"
            
            response["webhook_model"] = {
                "model_id": webhook_id_model,
                "model_type": model_type,
                "is_board": model_type == "board",
                "is_card": model_type == "card",
                "is_list": model_type == "list",
                "is_organization": model_type == "organization"
            }
        
        # Add webhook timeline
        response["webhook_timeline"] = {
            "created": webhook_date_created,
            "updated": webhook_date_updated,
            "first_failure": webhook_first_consecutive_fail_date,
            "age": "Unknown"  # Could calculate if we had current date
        }
        
        # Add webhook management information
        response["webhook_management"] = {
            "webhook_id": webhook_id,
            "callback_url": webhook_callback_url,
            "is_active": webhook_active,
            "needs_attention": webhook_consecutive_failures > 0,
            "failure_count": webhook_consecutive_failures,
            "description": webhook_description or "No description provided"
        }
        
        # Add webhook troubleshooting information
        if webhook_consecutive_failures > 0:
            response["webhook_troubleshooting"] = {
                "has_failures": True,
                "failure_count": webhook_consecutive_failures,
                "first_failure_date": webhook_first_consecutive_fail_date,
                "recommendations": [
                    "Check if the callback URL is accessible",
                    "Verify the callback URL responds to HEAD requests",
                    "Ensure the callback URL returns a 200 status code",
                    "Check webhook logs for detailed error information"
                ]
            }
        else:
            response["webhook_troubleshooting"] = {
                "has_failures": False,
                "status": "Webhook is functioning normally",
                "recommendations": [
                    "Monitor webhook performance regularly",
                    "Keep callback URL accessible and responsive"
                ]
            }
        
        # Add security information
        response["security_info"] = {
            "note": f"Webhook details retrieved for webhook {idWebhook}",
            "data_type": "Webhook configuration and status data",
            "sensitivity": "Webhook URLs and configuration (no sensitive credentials)",
            "webhook_id": webhook_id
        }
        
        # Add helpful information
        if webhook_active:
            if webhook_consecutive_failures > 0:
                response["note"] = f"Webhook {idWebhook} is active but has {webhook_consecutive_failures} consecutive failures"
            else:
                response["note"] = f"Webhook {idWebhook} is active and healthy"
        else:
            response["note"] = f"Webhook {idWebhook} is inactive"
        
        return response
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve webhook: {str(e)}",
            "action": "get_webhook_by_id",
            "webhook_id": idWebhook,
            "message": f"Failed to retrieve webhook {idWebhook}"
        }


@mcp.tool(
    "TRELLO_GET_TYPES_BY_ID",
    description="Get type by id. Retrieves the structural details of a trello object type (e.g., 'action', 'board', 'card') using its identifier; describes the type itself, not specific instances.",
)
def TRELLO_GET_TYPES_BY_ID(
    id: Annotated[str, "The identifier of the Trello object type to retrieve structural details for (e.g., 'action', 'board', 'card', 'list', 'member', 'organization', 'webhook')."]
):
    """Get type by id. Retrieves the structural details of a trello object type (e.g., 'action', 'board', 'card') using its identifier; describes the type itself, not specific instances."""
    err = _validate_required({"id": id}, ["id"])
    if err:
        return err
    
    try:
        # Try to get type information by ID
        endpoint = f"/types/{id}"
        
        # Make the API request
        result = trello_request("GET", endpoint)
        
        # Check if the result is an error or invalid response
        if not isinstance(result, dict) or result.get("error"):
            # The /types/{id} endpoint might not exist, so we'll provide alternative information
            return {
                "successful": False,
                "error": f"Type endpoint '/types/{id}' not available or invalid type ID",
                "action": "get_type_by_id",
                "type_id": id,
                "message": f"Failed to retrieve type {id} - endpoint may not exist",
                "alternative_approach": "Use specific object endpoints to understand structure",
                "suggested_endpoints": {
                    "board": "/boards/{boardId}",
                    "card": "/cards/{cardId}",
                    "list": "/lists/{listId}",
                    "member": "/members/{memberId}",
                    "organization": "/organizations/{orgId}",
                    "action": "/actions/{actionId}",
                    "webhook": "/webhooks/{webhookId}"
                },
                "note": "Trello API may not have a dedicated types endpoint. Use specific object endpoints instead."
            }
        
        # Extract key information
        type_id = result.get("id")
        type_name = result.get("name")
        type_display_name = result.get("displayName")
        type_description = result.get("description")
        type_fields = result.get("fields", [])
        type_actions = result.get("actions", [])
        type_attributes = result.get("attributes", [])
        type_relationships = result.get("relationships", [])
        
        response = {
            "successful": True,
            "data": result,
            "action": "get_type_by_id",
            "type_id": type_id,
            "type_name": type_name,
            "type_display_name": type_display_name,
            "message": f"Successfully retrieved type {id}"
        }
        
        # Add type summary
        response["type_summary"] = {
            "id": type_id,
            "name": type_name,
            "display_name": type_display_name,
            "description": type_description
        }
        
        # Add type structure information
        response["type_structure"] = {
            "fields_count": len(type_fields) if isinstance(type_fields, list) else 0,
            "actions_count": len(type_actions) if isinstance(type_actions, list) else 0,
            "attributes_count": len(type_attributes) if isinstance(type_attributes, list) else 0,
            "relationships_count": len(type_relationships) if isinstance(type_relationships, list) else 0
        }
        
        # Add fields information
        if isinstance(type_fields, list) and type_fields:
            response["type_fields"] = {
                "count": len(type_fields),
                "fields": type_fields,
                "field_names": [field.get("name") for field in type_fields if field.get("name")],
                "required_fields": [field for field in type_fields if field.get("required", False)],
                "optional_fields": [field for field in type_fields if not field.get("required", False)]
            }
        else:
            response["type_fields"] = {
                "count": 0,
                "note": "No fields defined for this type"
            }
        
        # Add actions information
        if isinstance(type_actions, list) and type_actions:
            response["type_actions"] = {
                "count": len(type_actions),
                "actions": type_actions,
                "action_names": [action.get("name") for action in type_actions if action.get("name")],
                "available_operations": [action.get("name") for action in type_actions if action.get("name")]
            }
        else:
            response["type_actions"] = {
                "count": 0,
                "note": "No actions defined for this type"
            }
        
        # Add attributes information
        if isinstance(type_attributes, list) and type_attributes:
            response["type_attributes"] = {
                "count": len(type_attributes),
                "attributes": type_attributes,
                "attribute_names": [attr.get("name") for attr in type_attributes if attr.get("name")]
            }
        else:
            response["type_attributes"] = {
                "count": 0,
                "note": "No attributes defined for this type"
            }
        
        # Add relationships information
        if isinstance(type_relationships, list) and type_relationships:
            response["type_relationships"] = {
                "count": len(type_relationships),
                "relationships": type_relationships,
                "relationship_names": [rel.get("name") for rel in type_relationships if rel.get("name")],
                "related_types": [rel.get("type") for rel in type_relationships if rel.get("type")]
            }
        else:
            response["type_relationships"] = {
                "count": 0,
                "note": "No relationships defined for this type"
            }
        
        # Add type analysis
        response["type_analysis"] = {
            "is_well_defined": len(type_fields) > 0 or len(type_actions) > 0,
            "has_fields": len(type_fields) > 0 if isinstance(type_fields, list) else False,
            "has_actions": len(type_actions) > 0 if isinstance(type_actions, list) else False,
            "has_attributes": len(type_attributes) > 0 if isinstance(type_attributes, list) else False,
            "has_relationships": len(type_relationships) > 0 if isinstance(type_relationships, list) else False,
            "complexity_score": (len(type_fields) if isinstance(type_fields, list) else 0) + 
                              (len(type_actions) if isinstance(type_actions, list) else 0) + 
                              (len(type_attributes) if isinstance(type_attributes, list) else 0) + 
                              (len(type_relationships) if isinstance(type_relationships, list) else 0)
        }
        
        # Add type metadata
        response["type_metadata"] = {
            "type_identifier": type_id,
            "type_name": type_name,
            "display_name": type_display_name,
            "description": type_description,
            "api_endpoint": f"/types/{id}",
            "data_source": "Trello API type definition"
        }
        
        # Add helpful information
        if type_display_name:
            response["note"] = f"Type: {type_display_name} ({type_name})"
        elif type_name:
            response["note"] = f"Type: {type_name}"
        else:
            response["note"] = f"Type ID: {id}"
        
        # Add usage information
        response["usage_info"] = {
            "purpose": "Describes the structure and capabilities of Trello object types",
            "use_cases": [
                "Understanding object structure",
                "API development and integration",
                "Field validation and mapping",
                "Relationship understanding"
            ],
            "note": "This describes the type itself, not specific instances"
        }
        
        return response
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve type: {str(e)}",
            "action": "get_type_by_id",
            "type_id": id,
            "message": f"Failed to retrieve type {id}"
        }


@mcp.tool(
    "TRELLO_GET_WEBHOOKS_BY_ID_WEBHOOK",
    description="Get webhook by ID. Retrieves the full configuration and status for a specific trello webhook by its unique id; this action does not return past notification history.",
)
def TRELLO_GET_WEBHOOKS_BY_ID_WEBHOOK(
    idWebhook: Annotated[str, "The unique ID of the webhook to retrieve full configuration and status for."]
):
    """Get webhook by ID. Retrieves the full configuration and status for a specific trello webhook by its unique id; this action does not return past notification history."""
    err = _validate_required({"idWebhook": idWebhook}, ["idWebhook"])
    if err:
        return err
    
    try:
        # Get webhook information by ID
        endpoint = f"/webhooks/{idWebhook}"
        
        # Make the API request
        result = trello_request("GET", endpoint)
        
        if not isinstance(result, dict):
            return {
                "successful": False,
                "error": "Invalid webhook data received",
                "action": "get_webhook_by_id",
                "webhook_id": idWebhook,
                "message": f"Failed to retrieve webhook {idWebhook}"
            }
        
        # Extract key information
        webhook_id = result.get("id")
        webhook_callback_url = result.get("callbackURL")
        webhook_id_model = result.get("idModel")
        webhook_description = result.get("description")
        webhook_active = result.get("active", True)
        webhook_consecutive_failures = result.get("consecutiveFailures", 0)
        webhook_first_consecutive_fail_date = result.get("firstConsecutiveFailDate")
        webhook_date_created = result.get("dateCreated")
        webhook_date_updated = result.get("dateUpdated")
        webhook_last_attempt = result.get("lastAttempt")
        webhook_last_http_status = result.get("lastHttpStatus")
        webhook_last_response = result.get("lastResponse")
        
        response = {
            "successful": True,
            "data": result,
            "action": "get_webhook_by_id",
            "webhook_id": webhook_id,
            "webhook_callback_url": webhook_callback_url,
            "webhook_id_model": webhook_id_model,
            "webhook_description": webhook_description,
            "webhook_active": webhook_active,
            "message": f"Successfully retrieved webhook {idWebhook}"
        }
        
        # Add webhook configuration
        response["webhook_configuration"] = {
            "id": webhook_id,
            "callback_url": webhook_callback_url,
            "model_id": webhook_id_model,
            "description": webhook_description,
            "active": webhook_active,
            "created": webhook_date_created,
            "updated": webhook_date_updated
        }
        
        # Add webhook status information
        response["webhook_status"] = {
            "is_active": webhook_active,
            "status": "active" if webhook_active else "inactive",
            "consecutive_failures": webhook_consecutive_failures,
            "first_failure_date": webhook_first_consecutive_fail_date,
            "last_attempt": webhook_last_attempt,
            "last_http_status": webhook_last_http_status
        }
        
        # Add webhook health information
        response["webhook_health"] = {
            "consecutive_failures": webhook_consecutive_failures,
            "is_healthy": webhook_consecutive_failures == 0,
            "first_failure_date": webhook_first_consecutive_fail_date,
            "health_status": "healthy" if webhook_consecutive_failures == 0 else "unhealthy",
            "last_attempt": webhook_last_attempt,
            "last_http_status": webhook_last_http_status,
            "last_response": webhook_last_response
        }
        
        # Add webhook model analysis
        if webhook_id_model:
            model_type = "unknown"
            if "board" in webhook_id_model.lower():
                model_type = "board"
            elif "card" in webhook_id_model.lower():
                model_type = "card"
            elif "list" in webhook_id_model.lower():
                model_type = "list"
            elif "organization" in webhook_id_model.lower():
                model_type = "organization"
            
            response["webhook_model"] = {
                "model_id": webhook_id_model,
                "model_type": model_type,
                "is_board": model_type == "board",
                "is_card": model_type == "card",
                "is_list": model_type == "list",
                "is_organization": model_type == "organization"
            }
        
        # Add webhook timeline
        response["webhook_timeline"] = {
            "created": webhook_date_created,
            "updated": webhook_date_updated,
            "first_failure": webhook_first_consecutive_fail_date,
            "last_attempt": webhook_last_attempt
        }
        
        # Add webhook performance metrics
        response["webhook_performance"] = {
            "consecutive_failures": webhook_consecutive_failures,
            "last_http_status": webhook_last_http_status,
            "last_attempt": webhook_last_attempt,
            "last_response": webhook_last_response,
            "reliability": "high" if webhook_consecutive_failures == 0 else "low",
            "needs_attention": webhook_consecutive_failures > 0
        }
        
        # Add webhook management information
        response["webhook_management"] = {
            "webhook_id": webhook_id,
            "callback_url": webhook_callback_url,
            "is_active": webhook_active,
            "needs_attention": webhook_consecutive_failures > 0,
            "failure_count": webhook_consecutive_failures,
            "description": webhook_description or "No description provided",
            "model_being_monitored": webhook_id_model,
            "last_activity": webhook_last_attempt
        }
        
        # Add webhook troubleshooting information
        if webhook_consecutive_failures > 0:
            response["webhook_troubleshooting"] = {
                "has_failures": True,
                "failure_count": webhook_consecutive_failures,
                "first_failure_date": webhook_first_consecutive_fail_date,
                "last_http_status": webhook_last_http_status,
                "last_response": webhook_last_response,
                "recommendations": [
                    "Check if the callback URL is accessible",
                    "Verify the callback URL responds to HEAD requests",
                    "Ensure the callback URL returns a 200 status code",
                    "Check webhook logs for detailed error information",
                    "Verify the callback URL is publicly accessible",
                    "Test the callback URL manually to ensure it's working"
                ]
            }
        else:
            response["webhook_troubleshooting"] = {
                "has_failures": False,
                "status": "Webhook is functioning normally",
                "last_http_status": webhook_last_http_status,
                "recommendations": [
                    "Monitor webhook performance regularly",
                    "Keep callback URL accessible and responsive",
                    "Monitor for any future failures"
                ]
            }
        
        # Add webhook security information
        response["webhook_security"] = {
            "callback_url": webhook_callback_url,
            "is_publicly_accessible": True,  # Assumed since webhooks require public URLs
            "security_notes": [
                "Callback URL must be publicly accessible",
                "Ensure callback URL uses HTTPS for security",
                "Implement proper authentication in your webhook handler",
                "Validate webhook signatures if available"
            ]
        }
        
        # Add webhook monitoring information
        response["webhook_monitoring"] = {
            "webhook_id": webhook_id,
            "monitoring_status": "active" if webhook_active else "inactive",
            "failure_tracking": webhook_consecutive_failures > 0,
            "last_activity": webhook_last_attempt,
            "health_status": "healthy" if webhook_consecutive_failures == 0 else "unhealthy",
            "recommended_actions": [
                "Monitor webhook status regularly",
                "Set up alerts for consecutive failures",
                "Test webhook functionality periodically"
            ]
        }
        
        # Add helpful information
        if webhook_active:
            if webhook_consecutive_failures > 0:
                response["note"] = f"Webhook {idWebhook} is active but has {webhook_consecutive_failures} consecutive failures (last status: {webhook_last_http_status})"
            else:
                response["note"] = f"Webhook {idWebhook} is active and healthy (last status: {webhook_last_http_status})"
        else:
            response["note"] = f"Webhook {idWebhook} is inactive"
        
        return response
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve webhook: {str(e)}",
            "action": "get_webhook_by_id",
            "webhook_id": idWebhook,
            "message": f"Failed to retrieve webhook {idWebhook}"
        }


@mcp.tool(
    "TRELLO_GET_WEBHOOKS_BY_ID_WEBHOOK_BY_FIELD",
    description="Get webhook field by id. Gets a specific field's value from a trello webhook, avoiding retrieval of the full webhook object.",
)
def TRELLO_GET_WEBHOOKS_BY_ID_WEBHOOK_BY_FIELD(
    idWebhook: Annotated[str, "The unique ID of the webhook to retrieve the field from."],
    field: Annotated[str, "The specific field to retrieve from the webhook (e.g., id, callbackURL, idModel, description, active, consecutiveFailures, firstConsecutiveFailDate, dateCreated, dateUpdated, lastAttempt, lastHttpStatus, lastResponse)."]
):
    """Get webhook field by id. Gets a specific field's value from a trello webhook, avoiding retrieval of the full webhook object."""
    err = _validate_required({"idWebhook": idWebhook, "field": field}, ["idWebhook", "field"])
    if err:
        return err
    
    try:
        # Get webhook information by ID
        endpoint = f"/webhooks/{idWebhook}"
        
        # Make the API request
        result = trello_request("GET", endpoint)
        
        if not isinstance(result, dict):
            return {
                "successful": False,
                "error": "Invalid webhook data received",
                "action": "get_webhook_field",
                "webhook_id": idWebhook,
                "field": field,
                "message": f"Failed to retrieve webhook information for field '{field}'"
            }
        
        # Check if the requested field exists
        if field not in result:
            available_fields = list(result.keys())
            return {
                "successful": False,
                "error": f"Field '{field}' not found in webhook data",
                "action": "get_webhook_field",
                "webhook_id": idWebhook,
                "field": field,
                "available_fields": available_fields,
                "message": f"Field '{field}' is not available. Available fields: {', '.join(available_fields)}"
            }
        
        # Get the field value
        field_value = result.get(field)
        
        # Extract additional context for better response
        webhook_id = result.get("id")
        webhook_callback_url = result.get("callbackURL")
        webhook_active = result.get("active", True)
        
        response = {
            "successful": True,
            "data": {
                "field": field,
                "value": field_value,
                "webhook_id": webhook_id,
                "webhook_callback_url": webhook_callback_url
            },
            "action": "get_webhook_field",
            "webhook_id": idWebhook,
            "field": field,
            "field_value": field_value,
            "message": f"Successfully retrieved field '{field}' from webhook {idWebhook}"
        }
        
        # Add field-specific information
        response["field_info"] = {
            "field_name": field,
            "field_value": field_value,
            "field_type": type(field_value).__name__,
            "is_empty": field_value is None or field_value == "",
            "is_list": isinstance(field_value, list),
            "is_dict": isinstance(field_value, dict)
        }
        
        # Add webhook context
        response["webhook_context"] = {
            "webhook_id": webhook_id,
            "webhook_callback_url": webhook_callback_url,
            "webhook_active": webhook_active,
            "field_source": "Trello webhook data"
        }
        
        # Add helpful information based on field type
        if isinstance(field_value, list):
            response["field_analysis"] = {
                "type": "list",
                "count": len(field_value),
                "items": field_value[:5] if len(field_value) > 5 else field_value,
                "truncated": len(field_value) > 5
            }
        elif isinstance(field_value, dict):
            response["field_analysis"] = {
                "type": "dictionary",
                "keys": list(field_value.keys()),
                "key_count": len(field_value.keys())
            }
        elif isinstance(field_value, str):
            response["field_analysis"] = {
                "type": "string",
                "length": len(field_value),
                "is_empty": field_value == "",
                "is_url": field.lower() in ["callbackurl", "url"] and field_value != "",
                "is_date": "date" in field.lower() and field_value != ""
            }
        else:
            response["field_analysis"] = {
                "type": type(field_value).__name__,
                "value": field_value
            }
        
        # Add field-specific context based on common webhook fields
        if field == "callbackURL":
            response["field_context"] = {
                "description": "The callback URL where Trello sends webhook notifications",
                "is_url": True,
                "is_required": True,
                "security_note": "Must be publicly accessible and respond to HEAD requests"
            }
        elif field == "idModel":
            response["field_context"] = {
                "description": "The ID of the Trello model (board, card, etc.) being monitored",
                "is_model_id": True,
                "is_required": True,
                "monitors": "Trello object changes"
            }
        elif field == "active":
            response["field_context"] = {
                "description": "Whether the webhook is active or inactive",
                "is_boolean": True,
                "is_status": True,
                "values": ["true", "false"]
            }
        elif field == "consecutiveFailures":
            response["field_context"] = {
                "description": "Number of consecutive webhook delivery failures",
                "is_numeric": True,
                "is_health_indicator": True,
                "healthy_value": 0
            }
        elif field == "description":
            response["field_context"] = {
                "description": "Human-readable description of the webhook",
                "is_text": True,
                "is_optional": True,
                "purpose": "Helps identify the webhook's purpose"
            }
        elif field in ["dateCreated", "dateUpdated", "firstConsecutiveFailDate", "lastAttempt"]:
            response["field_context"] = {
                "description": f"Webhook {field} timestamp",
                "is_date": True,
                "is_timeline": True,
                "format": "ISO 8601 date string"
            }
        elif field in ["lastHttpStatus", "lastResponse"]:
            response["field_context"] = {
                "description": f"Webhook {field} information",
                "is_performance": True,
                "is_debugging": True,
                "purpose": "Helps troubleshoot webhook issues"
            }
        
        # Add validation information
        response["validation"] = {
            "webhook_valid": True,
            "field_exists": True,
            "field_accessible": True,
            "permissions_sufficient": True
        }
        
        # Add security information
        response["security_info"] = {
            "note": f"Field '{field}' retrieved from webhook {idWebhook}",
            "data_type": "Webhook field value",
            "sensitivity": "Webhook configuration data (no sensitive credentials)",
            "webhook_id": webhook_id
        }
        
        # Add helpful information
        if webhook_callback_url:
            response["note"] = f"Field '{field}' for webhook monitoring {webhook_callback_url}"
        else:
            response["note"] = f"Field '{field}' for webhook {idWebhook}"
        
        return response
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve webhook field: {str(e)}",
            "action": "get_webhook_field",
            "webhook_id": idWebhook,
            "field": field,
            "message": f"Failed to retrieve field '{field}' from webhook {idWebhook}"
        }


@mcp.tool(
    "TRELLO_GET_NOTIF_CREATOR_FIELD",
    description="Get notification creator field. Fetches a specific field of the member who created the specified trello notification.",
)
def TRELLO_GET_NOTIF_CREATOR_FIELD(
    id_notification: Annotated[str, "The ID of the notification to get the creator field for."],
    field: Annotated[str, "The specific field to retrieve from the notification creator (e.g., id, username, fullName, initials, avatarHash, email, bio, bioData, confirmed, memberType, url, gravatarHash, uploadedAvatarHash, prefs, trophies, uploadedAvatarId, premiumFeatures, idBoards, idOrganizations, loginTypes, newEmail, oneTimeMessagesDismissed, marketingOptIn, messagesDismissed, tags, savedSearches, idEnterprisesAdmin, idEnterprisesDeactivated, limits, marketingOptInDate, idPremOrgsAdmin, avatarSource, emailUnread, loginTypes, newEmail, oneTimeMessagesDismissed, marketingOptIn, messagesDismissed, tags, savedSearches, idEnterprisesAdmin, idEnterprisesDeactivated, limits, marketingOptInDate, idPremOrgsAdmin, avatarSource, emailUnread)."]
):
    """Get notification creator field. Fetches a specific field of the member who created the specified trello notification."""
    err = _validate_required({"id_notification": id_notification, "field": field}, ["id_notification", "field"])
    if err:
        return err
    
    try:
        # Get notification creator field
        endpoint = f"/notifications/{id_notification}/memberCreator"
        
        # Build query parameters
        params = {
            "fields": field
        }
        
        # Make the API request
        result = trello_request("GET", endpoint, params=params)
        
        if not isinstance(result, dict):
            return {
                "successful": False,
                "error": "Invalid notification creator data received",
                "action": "get_notification_creator_field",
                "notification_id": id_notification,
                "field": field,
                "message": f"Failed to retrieve notification creator field '{field}' for notification {id_notification}"
            }
        
        # Extract the specific field value
        field_value = result.get(field)
        
        response = {
            "successful": True,
            "data": result,
            "action": "get_notification_creator_field",
            "notification_id": id_notification,
            "field": field,
            "field_value": field_value,
            "message": f"Successfully retrieved notification creator field '{field}' for notification {id_notification}",
            "notification_creator": result
        }
        
        # Add field-specific information
        if field == "id":
            response["note"] = "Notification creator member ID"
            response["field_description"] = "Unique identifier of the member who created the notification"
        elif field == "username":
            response["note"] = "Notification creator username"
            response["field_description"] = "Username of the member who created the notification"
        elif field == "fullName":
            response["note"] = "Notification creator full name"
            response["field_description"] = "Full name of the member who created the notification"
        elif field == "initials":
            response["note"] = "Notification creator initials"
            response["field_description"] = "Initials of the member who created the notification"
        elif field == "avatarHash":
            response["note"] = "Notification creator avatar hash"
            response["field_description"] = "Avatar hash of the member who created the notification"
        elif field == "email":
            response["note"] = "Notification creator email"
            response["field_description"] = "Email address of the member who created the notification"
        elif field == "bio":
            response["note"] = "Notification creator bio"
            response["field_description"] = "Biography of the member who created the notification"
        elif field == "bioData":
            response["note"] = "Notification creator bio data"
            response["field_description"] = "Bio data of the member who created the notification"
        elif field == "confirmed":
            response["note"] = "Notification creator confirmation status"
            response["field_description"] = "Whether the member who created the notification has confirmed their account"
        elif field == "memberType":
            response["note"] = "Notification creator member type"
            response["field_description"] = "Type of the member who created the notification"
        elif field == "url":
            response["note"] = "Notification creator URL"
            response["field_description"] = "URL of the member who created the notification"
        elif field == "gravatarHash":
            response["note"] = "Notification creator gravatar hash"
            response["field_description"] = "Gravatar hash of the member who created the notification"
        elif field == "uploadedAvatarHash":
            response["note"] = "Notification creator uploaded avatar hash"
            response["field_description"] = "Uploaded avatar hash of the member who created the notification"
        elif field == "prefs":
            response["note"] = "Notification creator preferences"
            response["field_description"] = "Preferences of the member who created the notification"
        elif field == "trophies":
            response["note"] = "Notification creator trophies"
            response["field_description"] = "Trophies of the member who created the notification"
        elif field == "uploadedAvatarId":
            response["note"] = "Notification creator uploaded avatar ID"
            response["field_description"] = "Uploaded avatar ID of the member who created the notification"
        elif field == "premiumFeatures":
            response["note"] = "Notification creator premium features"
            response["field_description"] = "Premium features available to the member who created the notification"
        elif field == "idBoards":
            response["note"] = "Notification creator board IDs"
            response["field_description"] = "Board IDs associated with the member who created the notification"
        elif field == "idOrganizations":
            response["note"] = "Notification creator organization IDs"
            response["field_description"] = "Organization IDs associated with the member who created the notification"
        elif field == "loginTypes":
            response["note"] = "Notification creator login types"
            response["field_description"] = "Login types used by the member who created the notification"
        elif field == "newEmail":
            response["note"] = "Notification creator new email"
            response["field_description"] = "New email address of the member who created the notification"
        elif field == "oneTimeMessagesDismissed":
            response["note"] = "Notification creator one-time messages dismissed"
            response["field_description"] = "One-time messages dismissed by the member who created the notification"
        elif field == "marketingOptIn":
            response["note"] = "Notification creator marketing opt-in status"
            response["field_description"] = "Marketing opt-in status of the member who created the notification"
        elif field == "messagesDismissed":
            response["note"] = "Notification creator messages dismissed"
            response["field_description"] = "Messages dismissed by the member who created the notification"
        elif field == "tags":
            response["note"] = "Notification creator tags"
            response["field_description"] = "Tags associated with the member who created the notification"
        elif field == "savedSearches":
            response["note"] = "Notification creator saved searches"
            response["field_description"] = "Saved searches of the member who created the notification"
        elif field == "idEnterprisesAdmin":
            response["note"] = "Notification creator enterprise admin IDs"
            response["field_description"] = "Enterprise admin IDs for the member who created the notification"
        elif field == "idEnterprisesDeactivated":
            response["note"] = "Notification creator deactivated enterprise IDs"
            response["field_description"] = "Deactivated enterprise IDs for the member who created the notification"
        elif field == "limits":
            response["note"] = "Notification creator limits"
            response["field_description"] = "Limits for the member who created the notification"
        elif field == "marketingOptInDate":
            response["note"] = "Notification creator marketing opt-in date"
            response["field_description"] = "Marketing opt-in date for the member who created the notification"
        elif field == "idPremOrgsAdmin":
            response["note"] = "Notification creator premium organization admin IDs"
            response["field_description"] = "Premium organization admin IDs for the member who created the notification"
        elif field == "avatarSource":
            response["note"] = "Notification creator avatar source"
            response["field_description"] = "Avatar source for the member who created the notification"
        elif field == "emailUnread":
            response["note"] = "Notification creator email unread status"
            response["field_description"] = "Email unread status for the member who created the notification"
        else:
            response["note"] = f"Notification creator field '{field}' value"
            response["field_description"] = f"Value of field '{field}' for the member who created the notification"
        
        # Add helpful information
        if field_value is not None:
            if isinstance(field_value, str) and len(field_value) > 50:
                response["note"] = f"Field '{field}' value: {field_value[:50]}... (truncated)"
            else:
                response["note"] = f"Field '{field}' value: {field_value}"
        else:
            response["note"] = f"Field '{field}' not found or null for notification creator"
        
        # Add field analysis
        response["field_analysis"] = {
            "requested_field": field,
            "field_value": field_value,
            "field_type": type(field_value).__name__ if field_value is not None else "null",
            "field_exists": field_value is not None,
            "notification_id": id_notification
        }
        
        # Add notification context
        response["notification_context"] = {
            "notification_id": id_notification,
            "creator_field": field,
            "creator_field_value": field_value,
            "description": f"Field '{field}' from the member who created notification {id_notification}"
        }
        
        return response
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve notification creator field: {str(e)}",
            "action": "get_notification_creator_field",
            "notification_id": id_notification,
            "field": field,
            "message": f"Failed to retrieve notification creator field '{field}' for notification {id_notification}"
        }


@mcp.tool(
    "TRELLO_GET_NOTIFICATION_ORG_FIELD",
    description="Get notification organization field. Retrieves a specific field from the trello organization associated with a given notification, provided the notification is linked to an organization.",
)
def TRELLO_GET_NOTIFICATION_ORG_FIELD(
    id_notification: Annotated[str, "The ID of the notification to get the organization field for."],
    field: Annotated[str, "The specific field to retrieve from the organization (e.g., id, name, displayName, desc, descData, url, website, logoHash, products, powerUps, idTags, limits, premiumFeatures, creationMethod, billableMemberCount, idMemberCreator, idEnterprise, enterprise, memberships, invitations, invitations_memberships, prefs, labelNames, boards, billableCollaboratorCount, billableCollaboratorCountPerOrganization, idBoards, idMembers, limits, premiumFeatures, creationMethod, billableMemberCount, idMemberCreator, idEnterprise, enterprise, memberships, invitations, invitations_memberships, prefs, labelNames, boards, billableCollaboratorCount, billableCollaboratorCountPerOrganization, idBoards, idMembers)."]
):
    """Get notification organization field. Retrieves a specific field from the trello organization associated with a given notification, provided the notification is linked to an organization."""
    err = _validate_required({"id_notification": id_notification, "field": field}, ["id_notification", "field"])
    if err:
        return err
    
    try:
        # Get notification organization field
        endpoint = f"/notifications/{id_notification}/organization"
        
        # Build query parameters
        params = {
            "fields": field
        }
        
        # Make the API request
        result = trello_request("GET", endpoint, params=params)
        
        if not isinstance(result, dict):
            return {
                "successful": False,
                "error": "Invalid notification organization data received",
                "action": "get_notification_org_field",
                "notification_id": id_notification,
                "field": field,
                "message": f"Failed to retrieve notification organization field '{field}' for notification {id_notification}"
            }
        
        # Extract the specific field value
        field_value = result.get(field)
        
        response = {
            "successful": True,
            "data": result,
            "action": "get_notification_org_field",
            "notification_id": id_notification,
            "field": field,
            "field_value": field_value,
            "message": f"Successfully retrieved notification organization field '{field}' for notification {id_notification}",
            "notification_organization": result
        }
        
        # Add field-specific information
        if field == "id":
            response["note"] = "Notification organization ID"
            response["field_description"] = "Unique identifier of the organization associated with the notification"
        elif field == "name":
            response["note"] = "Notification organization name"
            response["field_description"] = "Name of the organization associated with the notification"
        elif field == "displayName":
            response["note"] = "Notification organization display name"
            response["field_description"] = "Display name of the organization associated with the notification"
        elif field == "desc":
            response["note"] = "Notification organization description"
            response["field_description"] = "Description of the organization associated with the notification"
        elif field == "descData":
            response["note"] = "Notification organization description data"
            response["field_description"] = "Description data of the organization associated with the notification"
        elif field == "url":
            response["note"] = "Notification organization URL"
            response["field_description"] = "URL of the organization associated with the notification"
        elif field == "website":
            response["note"] = "Notification organization website"
            response["field_description"] = "Website of the organization associated with the notification"
        elif field == "logoHash":
            response["note"] = "Notification organization logo hash"
            response["field_description"] = "Logo hash of the organization associated with the notification"
        elif field == "products":
            response["note"] = "Notification organization products"
            response["field_description"] = "Products available to the organization associated with the notification"
        elif field == "powerUps":
            response["note"] = "Notification organization power-ups"
            response["field_description"] = "Power-ups available to the organization associated with the notification"
        elif field == "idTags":
            response["note"] = "Notification organization tag IDs"
            response["field_description"] = "Tag IDs associated with the organization"
        elif field == "limits":
            response["note"] = "Notification organization limits"
            response["field_description"] = "Limits for the organization associated with the notification"
        elif field == "premiumFeatures":
            response["note"] = "Notification organization premium features"
            response["field_description"] = "Premium features available to the organization associated with the notification"
        elif field == "creationMethod":
            response["note"] = "Notification organization creation method"
            response["field_description"] = "Method used to create the organization associated with the notification"
        elif field == "billableMemberCount":
            response["note"] = "Notification organization billable member count"
            response["field_description"] = "Number of billable members in the organization associated with the notification"
        elif field == "idMemberCreator":
            response["note"] = "Notification organization creator member ID"
            response["field_description"] = "ID of the member who created the organization associated with the notification"
        elif field == "idEnterprise":
            response["note"] = "Notification organization enterprise ID"
            response["field_description"] = "Enterprise ID associated with the organization"
        elif field == "enterprise":
            response["note"] = "Notification organization enterprise data"
            response["field_description"] = "Enterprise data for the organization associated with the notification"
        elif field == "memberships":
            response["note"] = "Notification organization memberships"
            response["field_description"] = "Memberships in the organization associated with the notification"
        elif field == "invitations":
            response["note"] = "Notification organization invitations"
            response["field_description"] = "Invitations to the organization associated with the notification"
        elif field == "invitations_memberships":
            response["note"] = "Notification organization invitation memberships"
            response["field_description"] = "Invitation memberships for the organization associated with the notification"
        elif field == "prefs":
            response["note"] = "Notification organization preferences"
            response["field_description"] = "Preferences for the organization associated with the notification"
        elif field == "labelNames":
            response["note"] = "Notification organization label names"
            response["field_description"] = "Label names for the organization associated with the notification"
        elif field == "boards":
            response["note"] = "Notification organization boards"
            response["field_description"] = "Boards in the organization associated with the notification"
        elif field == "billableCollaboratorCount":
            response["note"] = "Notification organization billable collaborator count"
            response["field_description"] = "Number of billable collaborators in the organization associated with the notification"
        elif field == "billableCollaboratorCountPerOrganization":
            response["note"] = "Notification organization billable collaborator count per organization"
            response["field_description"] = "Billable collaborator count per organization for the notification"
        elif field == "idBoards":
            response["note"] = "Notification organization board IDs"
            response["field_description"] = "Board IDs in the organization associated with the notification"
        elif field == "idMembers":
            response["note"] = "Notification organization member IDs"
            response["field_description"] = "Member IDs in the organization associated with the notification"
        else:
            response["note"] = f"Notification organization field '{field}' value"
            response["field_description"] = f"Value of field '{field}' for the organization associated with the notification"
        
        # Add helpful information
        if field_value is not None:
            if isinstance(field_value, str) and len(field_value) > 50:
                response["note"] = f"Field '{field}' value: {field_value[:50]}... (truncated)"
            else:
                response["note"] = f"Field '{field}' value: {field_value}"
        else:
            response["note"] = f"Field '{field}' not found or null for notification organization"
        
        # Add field analysis
        response["field_analysis"] = {
            "requested_field": field,
            "field_value": field_value,
            "field_type": type(field_value).__name__ if field_value is not None else "null",
            "field_exists": field_value is not None,
            "notification_id": id_notification
        }
        
        # Add notification context
        response["notification_context"] = {
            "notification_id": id_notification,
            "organization_field": field,
            "organization_field_value": field_value,
            "description": f"Field '{field}' from the organization associated with notification {id_notification}"
        }
        
        return response
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve notification organization field: {str(e)}",
            "action": "get_notification_org_field",
            "notification_id": id_notification,
            "field": field,
            "message": f"Failed to retrieve notification organization field '{field}' for notification {id_notification}"
        }


@mcp.tool(
    "TRELLO_GET_NOTIFICATIONS_BOARD_BY_ID_NOTIFICATION",
    description="Get notification board by ID. Gets the trello board associated with a given notification id, returning only board data and allowing selection of specific board fields.",
)
def TRELLO_GET_NOTIFICATIONS_BOARD_BY_ID_NOTIFICATION(
    id_notification: Annotated[str, "The ID of the notification to get the board for."],
    fields: Annotated[str, "The fields to retrieve from the board (e.g., id, name, desc, closed, idOrganization, pinned, url, prefs, labelNames, shortLink, powerUps, dateLastActivity, dateLastView, shortUrl, idTags, datePluginDisable, creationMethod, ixUpdate, enterprise, limits, starred, descData, idBoardSource, idMemberCreator, idOrganization, pinned, url, prefs, labelNames, shortLink, powerUps, dateLastActivity, dateLastView, shortUrl, idTags, datePluginDisable, creationMethod, ixUpdate, enterprise, limits, starred, descData, idBoardSource, idMemberCreator). Defaults to all."] = "all"
):
    """Get notification board by ID. Gets the trello board associated with a given notification id, returning only board data and allowing selection of specific board fields."""
    err = _validate_required({"id_notification": id_notification}, ["id_notification"])
    if err:
        return err
    
    try:
        # Get notification board
        endpoint = f"/notifications/{id_notification}/board"
        
        # Build query parameters
        params = {}
        if fields is not None:
            params["fields"] = fields
        
        # Make the API request
        result = trello_request("GET", endpoint, params=params)
        
        if not isinstance(result, dict):
            return {
                "successful": False,
                "error": "Invalid notification board data received",
                "action": "get_notification_board",
                "notification_id": id_notification,
                "message": f"Failed to retrieve board for notification {id_notification}"
            }
        
        # Extract key information
        board_id = result.get("id")
        board_name = result.get("name")
        board_desc = result.get("desc")
        board_closed = result.get("closed")
        organization_id = result.get("idOrganization")
        board_url = result.get("url")
        board_short_url = result.get("shortUrl")
        
        response = {
            "successful": True,
            "data": result,
            "action": "get_notification_board",
            "notification_id": id_notification,
            "board_id": board_id,
            "board_name": board_name,
            "board_desc": board_desc,
            "board_closed": board_closed,
            "organization_id": organization_id,
            "board_url": board_url,
            "board_short_url": board_short_url,
            "message": f"Successfully retrieved board for notification {id_notification}",
            "notification_board": result
        }
        
        # Add board-specific information
        if board_name:
            response["note"] = f"Board '{board_name}' associated with notification {id_notification}"
        else:
            response["note"] = f"Board {board_id} associated with notification {id_notification}"
        
        # Add board context
        response["board_context"] = {
            "notification_id": id_notification,
            "board_id": board_id,
            "board_name": board_name,
            "board_closed": board_closed,
            "organization_id": organization_id,
            "description": f"Board associated with notification {id_notification}"
        }
        
        # Add field analysis
        response["field_analysis"] = {
            "requested_fields": fields,
            "board_id": board_id,
            "board_name": board_name,
            "board_closed": board_closed,
            "organization_id": organization_id,
            "notification_id": id_notification
        }
        
        # Add helpful information
        if board_url:
            response["board_urls"] = {
                "full_url": board_url,
                "short_url": board_short_url
            }
        
        if organization_id:
            response["organization_info"] = {
                "organization_id": organization_id,
                "note": "This board belongs to an organization"
            }
        else:
            response["organization_info"] = {
                "note": "This board is not part of an organization"
            }
        
        return response
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve notification board: {str(e)}",
            "action": "get_notification_board",
            "notification_id": id_notification,
            "message": f"Failed to retrieve board for notification {id_notification}"
        }


@mcp.tool(
    "TRELLO_GET_BOARDS_MEMBERSHIPS_BY_ID_BOARD_BY_ID_MEMBERSHIP",
    description="Get board membership. Retrieves a specific membership on a trello board by its id, optionally including member details.",
)
def TRELLO_GET_BOARDS_MEMBERSHIPS_BY_ID_BOARD_BY_ID_MEMBERSHIP(
    id_board: Annotated[str, "The ID of the board containing the membership."],
    id_membership: Annotated[str, "The ID of the membership to retrieve."],
    member: Annotated[str, "Include member details."] = "",
    member_fields: Annotated[str, "Comma-separated list of member fields. Defaults to fullName and username."] = "fullName,username"
):
    """Get board membership. Retrieves a specific membership on a trello board by its id, optionally including member details."""
    err = _validate_required({"id_board": id_board, "id_membership": id_membership}, ["id_board", "id_membership"])
    if err:
        return err
    
    # Build the endpoint
    endpoint = f"/boards/{id_board}/memberships/{id_membership}"
    
    # Build query parameters
    params = {}
    
    # Add parameters only if they have values and are not defaults
    if member and member.strip():
        params["member"] = member.strip()
    if member_fields and member_fields.strip() and member_fields != "fullName,username":
        params["member_fields"] = member_fields.strip()
    
    # Make the API request
    result = trello_request("GET", endpoint, params=params)
    
    if not isinstance(result, dict):
        return {
            "successful": False,
            "error": "Invalid membership data received",
            "action": "get_board_membership",
            "board_id": id_board,
            "membership_id": id_membership,
            "message": f"Failed to retrieve membership {id_membership} from board {id_board}"
        }
    
    return {
        "successful": True,
        "data": result,
        "action": "get_board_membership",
        "board_id": id_board,
        "membership_id": id_membership,
        "member_fields": member_fields,
        "message": f"Successfully retrieved membership {id_membership} from board {id_board}"
    }


@mcp.tool(
    "TRELLO_GET_BOARDS_MEMBERSHIPS_BY_ID_BOARD",
    description="List board memberships. Retrieves trello board memberships (user roles and permissions) for auditing access or managing collaboration, returning only membership data and not other board content.",
)
def TRELLO_GET_BOARDS_MEMBERSHIPS_BY_ID_BOARD(
    id_board: Annotated[str, "The ID of the board to get memberships from."],
    filter: Annotated[str, "Filter memberships. Defaults to all."] = "all",
    member: Annotated[str, "Filter by specific member."] = "",
    member_fields: Annotated[str, "Comma-separated list of member fields. Defaults to fullName and username."] = "fullName,username"
):
    """List board memberships. Retrieves trello board memberships (user roles and permissions) for auditing access or managing collaboration, returning only membership data and not other board content."""
    err = _validate_required({"id_board": id_board}, ["id_board"])
    if err:
        return err
    
    # Build the endpoint
    endpoint = f"/boards/{id_board}/memberships"
    
    # Build query parameters
    params = {}
    
    # Add parameters only if they have values and are not defaults
    if filter and filter.strip() and filter.lower() != "all":
        params["filter"] = filter.strip()
    if member and member.strip():
        params["member"] = member.strip()
    if member_fields and member_fields.strip() and member_fields != "fullName,username":
        params["member_fields"] = member_fields.strip()
    
    # Make the API request
    result = trello_request("GET", endpoint, params=params)
    
    if not isinstance(result, list):
        return {
            "successful": False,
            "error": "Invalid memberships data received",
            "action": "get_board_memberships",
            "board_id": id_board,
            "message": f"Failed to retrieve memberships from board {id_board}"
        }
    
    return {
        "successful": True,
        "data": result,
        "action": "get_board_memberships",
        "board_id": id_board,
        "membership_count": len(result),
        "filter": filter,
        "member_fields": member_fields,
        "message": f"Successfully retrieved {len(result)} memberships from board {id_board}"
    }


@mcp.tool(
    "TRELLO_UPDATE_BOARD_MEMBERSHIP",
    description="Update board membership. Updates a user's role (e.g., admin, normal, observer) on a specific trello board or retrieves updated member details, requiring existing board and membership ids.",
)
def TRELLO_UPDATE_BOARD_MEMBERSHIP(
    id_board: Annotated[str, "The ID of the board containing the membership."],
    id_membership: Annotated[str, "The ID of the membership to update."],
    type: Annotated[str, "The new role type for the membership (e.g., admin, normal, observer)."],
    member_fields: Annotated[str, "Comma-separated list of member fields to return. Defaults to fullName and username."] = "fullName,username"
):
    """Update board membership. Updates a user's role (e.g., admin, normal, observer) on a specific trello board or retrieves updated member details, requiring existing board and membership ids."""
    err = _validate_required({"id_board": id_board, "id_membership": id_membership, "type": type}, ["id_board", "id_membership", "type"])
    if err:
        return err
    
    try:
        endpoint = f"/boards/{id_board}/memberships/{id_membership}"
        
        # Build data payload
        data = {
            "type": type
        }
        
        # Build query parameters for member fields
        params = {}
        if member_fields and member_fields.strip():
            params["member_fields"] = member_fields.strip()
        
        result = trello_request("PUT", endpoint, data=data, params=params)
        
        return {
            "successful": True,
            "data": result,
            "action": "update_board_membership",
            "board_id": id_board,
            "membership_id": id_membership,
            "new_role": type,
            "message": f"Successfully updated membership {id_membership} on board {id_board} to role '{type}'"
        }
    except Exception as e:
        error_message = str(e)
        
        # Provide specific guidance for common errors
        if "403" in error_message:
            return {
                "successful": False,
                "error": f"Permission denied: {error_message}",
                "action": "update_board_membership",
                "board_id": id_board,
                "membership_id": id_membership,
                "message": f"Failed to update membership {id_membership} - insufficient permissions",
                "guidance": "You must be an admin of the board to update memberships.",
                "suggestion": "Verify you have admin access to the board or ask a board admin to make the change."
            }
        elif "404" in error_message:
            return {
                "successful": False,
                "error": f"Membership not found: {error_message}",
                "action": "update_board_membership",
                "board_id": id_board,
                "membership_id": id_membership,
                "message": f"Failed to update membership {id_membership} - membership not found",
                "guidance": "The membership ID may be invalid or the membership may have been removed.",
                "suggestion": "Verify the membership ID is correct and the membership still exists."
            }
        elif "400" in error_message and "type" in error_message.lower():
            return {
                "successful": False,
                "error": f"Invalid role type: {error_message}",
                "action": "update_board_membership",
                "board_id": id_board,
                "membership_id": id_membership,
                "message": f"Failed to update membership {id_membership} - invalid role type '{type}'",
                "guidance": "Valid role types are: admin, normal, observer.",
                "suggestion": "Use one of the valid role types: admin, normal, or observer."
            }
        else:
            return {
                "successful": False,
                "error": f"Failed to update board membership: {error_message}",
                "action": "update_board_membership",
                "board_id": id_board,
                "membership_id": id_membership,
                "message": f"Failed to update membership {id_membership} on board {id_board}"
            }

@mcp.tool(
    "TRELLO_GET_BOARDS_MEMBERS_BY_ID_BOARD_BY_FILTER",
    description="Get board members filtered. Retrieves members of a trello board using a specified filter, assuming the board exists and the filter is valid.",
)
def TRELLO_GET_BOARDS_MEMBERS_BY_ID_BOARD_BY_FILTER(
    id_board: Annotated[str, "The ID of the board to get members from."],
    filter: Annotated[str, "Filter members by type (e.g., 'normal', 'admins', 'owners')."]
):
    """Get board members filtered. Retrieves members of a trello board using a specified filter, assuming the board exists and the filter is valid."""
    err = _validate_required({"id_board": id_board, "filter": filter}, ["id_board", "filter"])
    if err:
        return err
    
    # Build the endpoint
    endpoint = f"/boards/{id_board}/members"
    
    # Build query parameters
    params = {"filter": filter}
    
    # Make the API request
    result = trello_request("GET", endpoint, params=params)
    
    if not isinstance(result, list):
        return {
            "successful": False,
            "error": "Invalid members data received",
            "action": "get_board_members_by_filter",
            "board_id": id_board,
            "filter": filter,
            "message": f"Failed to retrieve members from board {id_board} with filter '{filter}'"
        }
    
    return {
        "successful": True,
        "data": result,
        "action": "get_board_members_by_filter",
        "board_id": id_board,
        "filter": filter,
        "member_count": len(result),
        "message": f"Successfully retrieved {len(result)} members from board {id_board} with filter '{filter}'"
    }


@mcp.tool(
    "TRELLO_GET_BOARDS_MEMBERS_BY_ID_BOARD",
    description="Get board members. Retrieves members of a trello board, with options to filter the list and select specific member fields to return.",
)
def TRELLO_GET_BOARDS_MEMBERS_BY_ID_BOARD(
    id_board: Annotated[str, "The ID of the board to get members from."],
    activity: Annotated[str, "Include member activity information."] = "",
    fields: Annotated[str, "Comma-separated list of member fields. Defaults to fullName and username."] = "fullName,username",
    filter: Annotated[str, "Filter members. Defaults to normal."] = "normal"
):
    """Get board members. Retrieves members of a trello board, with options to filter the list and select specific member fields to return."""
    err = _validate_required({"id_board": id_board}, ["id_board"])
    if err:
        return err
    
    # Build the endpoint
    endpoint = f"/boards/{id_board}/members"
    
    # Build query parameters
    params = {}
    
    # Add parameters only if they have values and are not defaults
    if activity and activity.strip():
        params["activity"] = activity.strip()
    if fields and fields.strip() and fields != "fullName,username":
        params["fields"] = fields.strip()
    if filter and filter.strip() and filter.lower() != "normal":
        params["filter"] = filter.strip()
    
    # Make the API request
    result = trello_request("GET", endpoint, params=params)
    
    if not isinstance(result, list):
        return {
            "successful": False,
            "error": "Invalid members data received",
            "action": "get_board_members",
            "board_id": id_board,
            "message": f"Failed to retrieve members from board {id_board}"
        }
    
    return {
        "successful": True,
        "data": result,
        "action": "get_board_members",
        "board_id": id_board,
        "member_count": len(result),
        "filter": filter,
        "fields": fields,
        "message": f"Successfully retrieved {len(result)} members from board {id_board}"
    }


@mcp.tool(
    "TRELLO_GET_BOARDS_LISTS_BY_ID_BOARD_BY_FILTER",
    description="Get board lists by filter. Fetches lists by status from an accessible trello board; card details for these lists require a separate call.",
)
def TRELLO_GET_BOARDS_LISTS_BY_ID_BOARD_BY_FILTER(
    id_board: Annotated[str, "The ID of the board to get lists from."],
    filter: Annotated[str, "Filter lists by status (e.g., 'open', 'closed', 'all')."]
):
    """Get board lists by filter. Fetches lists by status from an accessible trello board; card details for these lists require a separate call."""
    err = _validate_required({"id_board": id_board, "filter": filter}, ["id_board", "filter"])
    if err:
        return err
    
    # Build the endpoint
    endpoint = f"/boards/{id_board}/lists"
    
    # Build query parameters
    params = {"filter": filter}
    
    # Make the API request
    result = trello_request("GET", endpoint, params=params)
    
    if not isinstance(result, list):
        return {
            "successful": False,
            "error": "Invalid lists data received",
            "action": "get_board_lists_by_filter",
            "board_id": id_board,
            "filter": filter,
            "message": f"Failed to retrieve lists from board {id_board} with filter '{filter}'"
        }
    
    return {
        "successful": True,
        "data": result,
        "action": "get_board_lists_by_filter",
        "board_id": id_board,
        "filter": filter,
        "list_count": len(result),
        "message": f"Successfully retrieved {len(result)} lists from board {id_board} with filter '{filter}'"
    }


@mcp.tool(
    "TRELLO_GET_BOARDS_LISTS_BY_ID_BOARD",
    description="Get board's lists. Retrieves lists from a specified trello board, with options to filter lists and include card details.",
)
def TRELLO_GET_BOARDS_LISTS_BY_ID_BOARD(
    id_board: Annotated[str, "The ID of the board to get lists from."],
    card_fields: Annotated[str, "Comma-separated list of card fields. Defaults to all."] = "all",
    cards: Annotated[str, "Include cards. Defaults to none."] = "none",
    fields: Annotated[str, "Comma-separated list of list fields. Defaults to all."] = "all",
    filter: Annotated[str, "Filter lists. Defaults to open."] = "open"
):
    """Get board's lists. Retrieves lists from a specified trello board, with options to filter lists and include card details."""
    err = _validate_required({"id_board": id_board}, ["id_board"])
    if err:
        return err
    
    # Build the endpoint
    endpoint = f"/boards/{id_board}/lists"
    
    # Build query parameters
    params = {}
    
    # Add parameters only if they have values and are not defaults
    if card_fields and card_fields.strip() and card_fields.lower() != "all":
        params["card_fields"] = card_fields.strip()
    if cards and cards.strip() and cards.lower() != "none":
        params["cards"] = cards.strip()
    if fields and fields.strip() and fields.lower() != "all":
        params["fields"] = fields.strip()
    if filter and filter.strip() and filter.lower() != "open":
        params["filter"] = filter.strip()
    
    # Make the API request
    result = trello_request("GET", endpoint, params=params)
    
    if not isinstance(result, list):
        return {
            "successful": False,
            "error": "Invalid lists data received",
            "action": "get_board_lists",
            "board_id": id_board,
            "message": f"Failed to retrieve lists from board {id_board}"
        }
    
    return {
        "successful": True,
        "data": result,
        "action": "get_board_lists",
        "board_id": id_board,
        "list_count": len(result),
        "filter": filter,
        "fields": fields,
        "message": f"Successfully retrieved {len(result)} lists from board {id_board}"
    }


@mcp.tool(
    "TRELLO_GET_BOARDS_LABELS_BY_ID_BOARD_BY_ID_LABEL",
    description="Get a board label. Fetches specified fields for a specific label on a trello board; this read-only action does not return information about which cards the label is attached to.",
)
def TRELLO_GET_BOARDS_LABELS_BY_ID_BOARD_BY_ID_LABEL(
    id_board: Annotated[str, "The ID of the board containing the label."],
    id_label: Annotated[str, "The ID of the label to retrieve."],
    fields: Annotated[str, "Comma-separated list of label fields. Defaults to all."] = "all"
):
    """Get a board label. Fetches specified fields for a specific label on a trello board; this read-only action does not return information about which cards the label is attached to."""
    err = _validate_required({"id_board": id_board, "id_label": id_label}, ["id_board", "id_label"])
    if err:
        return err
    
    # Build the endpoint
    endpoint = f"/boards/{id_board}/labels/{id_label}"
    
    # Build query parameters
    params = {}
    
    # Add fields parameter only if it's not the default
    if fields and fields.strip() and fields.lower() != "all":
        params["fields"] = fields.strip()
    
    # Make the API request
    result = trello_request("GET", endpoint, params=params)
    
    if not isinstance(result, dict):
        return {
            "successful": False,
            "error": "Invalid label data received",
            "action": "get_board_label",
            "board_id": id_board,
            "label_id": id_label,
            "message": f"Failed to retrieve label {id_label} from board {id_board}"
        }
    
    return {
        "successful": True,
        "data": result,
        "action": "get_board_label",
        "board_id": id_board,
        "label_id": id_label,
        "fields": fields,
        "label_name": result.get("name"),
        "label_color": result.get("color"),
        "message": f"Successfully retrieved label {id_label} from board {id_board}"
    }


@mcp.tool(
    "TRELLO_GET_BOARDS_LABELS_BY_ID_BOARD",
    description="Get board labels by ID. Fetches labels for a specified trello board, aiding in its organization or label management; this action does not detail per-card label usage.",
)
def TRELLO_GET_BOARDS_LABELS_BY_ID_BOARD(
    id_board: Annotated[str, "The ID of the board to get labels from."],
    fields: Annotated[str, "Comma-separated list of label fields. Defaults to all."] = "all",
    limit: Annotated[str, "Maximum number of labels to return. Defaults to 50."] = "50"
):
    """Get board labels by ID. Fetches labels for a specified trello board, aiding in its organization or label management; this action does not detail per-card label usage."""
    err = _validate_required({"id_board": id_board}, ["id_board"])
    if err:
        return err
    
    # Build the endpoint
    endpoint = f"/boards/{id_board}/labels"
    
    # Build query parameters
    params = {}
    
    # Add parameters only if they have values and are not defaults
    if fields and fields.strip() and fields.lower() != "all":
        params["fields"] = fields.strip()
    if limit and limit.strip() and limit != "50":
        params["limit"] = limit.strip()
    
    # Make the API request
    result = trello_request("GET", endpoint, params=params)
    
    if not isinstance(result, list):
        return {
            "successful": False,
            "error": "Invalid labels data received",
            "action": "get_board_labels",
            "board_id": id_board,
            "message": f"Failed to retrieve labels from board {id_board}"
        }
    
    return {
        "successful": True,
        "data": result,
        "action": "get_board_labels",
        "board_id": id_board,
        "label_count": len(result),
        "fields": fields,
        "limit": limit,
        "message": f"Successfully retrieved {len(result)} labels from board {id_board}"
    }


@mcp.tool(
    "TRELLO_GET_BOARDS_DELTAS_BY_ID_BOARD",
    description="Retrieve board deltas. Retrieves recent changes (deltas) for a trello board by its id, allowing tracking of modifications since a specified update sequence number (`ixlastupdate`).",
)
def TRELLO_GET_BOARDS_DELTAS_BY_ID_BOARD(
    id_board: Annotated[str, "The ID of the board to get deltas from."],
    ix_last_update: Annotated[str, "The last update sequence number to track changes since."],
    tags: Annotated[str, "Comma-separated list of tags to filter deltas."]
):
    """Retrieve board deltas. Retrieves recent changes (deltas) for a trello board by its id, allowing tracking of modifications since a specified update sequence number (`ixlastupdate`)."""
    err = _validate_required({"id_board": id_board, "ix_last_update": ix_last_update, "tags": tags}, ["id_board", "ix_last_update", "tags"])
    if err:
        return err
    
    # Build the endpoint
    endpoint = f"/boards/{id_board}/deltas"
    
    # Build query parameters
    params = {
        "ixLastUpdate": ix_last_update,
        "tags": tags
    }
    
    # Make the API request
    result = trello_request("GET", endpoint, params=params)
    
    if not isinstance(result, (dict, list)):
        return {
            "successful": False,
            "error": "Invalid deltas data received",
            "action": "get_board_deltas",
            "board_id": id_board,
            "ix_last_update": ix_last_update,
            "tags": tags,
            "message": f"Failed to retrieve deltas from board {id_board}"
        }
    
    return {
        "successful": True,
        "data": result,
        "action": "get_board_deltas",
        "board_id": id_board,
        "ix_last_update": ix_last_update,
        "tags": tags,
        "message": f"Successfully retrieved deltas from board {id_board} since update {ix_last_update}"
    }


@mcp.tool(
    "TRELLO_GET_BOARDS_CHECKLISTS_BY_ID_BOARD",
    description="Get board checklists. Retrieves checklists (primarily structure/metadata, not detailed item history) from a trello board, with options to include associated card and check item details and to control which fields are returned for each entity.",
)
def TRELLO_GET_BOARDS_CHECKLISTS_BY_ID_BOARD(
    id_board: Annotated[str, "The ID of the board to get checklists from."],
    card_fields: Annotated[str, "Comma-separated list of card fields. Defaults to all."] = "all",
    cards: Annotated[str, "Include cards. Defaults to none."] = "none",
    check_item_fields: Annotated[str, "Comma-separated list of check item fields. Defaults to name, nameData, pos and state."] = "name,nameData,pos,state",
    check_items: Annotated[str, "Include check items. Defaults to all."] = "all",
    fields: Annotated[str, "Comma-separated list of checklist fields. Defaults to all."] = "all",
    filter: Annotated[str, "Filter checklists. Defaults to all."] = "all"
):
    """Get board checklists. Retrieves checklists (primarily structure/metadata, not detailed item history) from a trello board, with options to include associated card and check item details and to control which fields are returned for each entity."""
    err = _validate_required({"id_board": id_board}, ["id_board"])
    if err:
        return err
    
    # Build the endpoint
    endpoint = f"/boards/{id_board}/checklists"
    
    # Build query parameters
    params = {}
    
    # Add parameters only if they have values and are not defaults
    if card_fields and card_fields.strip() and card_fields.lower() != "all":
        params["card_fields"] = card_fields.strip()
    if cards and cards.strip() and cards.lower() != "none":
        params["cards"] = cards.strip()
    if check_item_fields and check_item_fields.strip() and check_item_fields != "name,nameData,pos,state":
        params["checkItem_fields"] = check_item_fields.strip()
    if check_items and check_items.strip() and check_items.lower() != "all":
        params["checkItems"] = check_items.strip()
    if fields and fields.strip() and fields.lower() != "all":
        params["fields"] = fields.strip()
    if filter and filter.strip() and filter.lower() != "all":
        params["filter"] = filter.strip()
    
    # Make the API request
    result = trello_request("GET", endpoint, params=params)
    
    if not isinstance(result, list):
        return {
            "successful": False,
            "error": "Invalid checklists data received",
            "action": "get_board_checklists",
            "board_id": id_board,
            "message": f"Failed to retrieve checklists from board {id_board}"
        }
    
    return {
        "successful": True,
        "data": result,
        "action": "get_board_checklists",
        "board_id": id_board,
        "checklist_count": len(result),
        "filter": filter,
        "fields": fields,
        "message": f"Successfully retrieved {len(result)} checklists from board {id_board}"
    }


@mcp.tool(
    "TRELLO_GET_BOARDS_CARDS_BY_ID_BOARD_BY_FILTER",
    description="Get cards by filter from board. Retrieves cards from a specified trello board, filtered by 'all', 'closed', 'none', 'open', or 'visible'.",
)
def TRELLO_GET_BOARDS_CARDS_BY_ID_BOARD_BY_FILTER(
    id_board: Annotated[str, "The ID of the board to get cards from."],
    filter: Annotated[str, "Filter cards by 'all', 'closed', 'none', 'open', or 'visible'."]
):
    """Get cards by filter from board. Retrieves cards from a specified trello board, filtered by 'all', 'closed', 'none', 'open', or 'visible'."""
    err = _validate_required({"id_board": id_board, "filter": filter}, ["id_board", "filter"])
    if err:
        return err
    
    # Build the endpoint
    endpoint = f"/boards/{id_board}/cards"
    
    # Build query parameters
    params = {"filter": filter}
    
    # Make the API request
    result = trello_request("GET", endpoint, params=params)
    
    if not isinstance(result, list):
        return {
            "successful": False,
            "error": "Invalid cards data received",
            "action": "get_cards_by_filter",
            "board_id": id_board,
            "filter": filter,
            "message": f"Failed to retrieve cards from board {id_board} with filter '{filter}'"
        }
    
    return {
        "successful": True,
        "data": result,
        "action": "get_cards_by_filter",
        "board_id": id_board,
        "filter": filter,
        "card_count": len(result),
        "message": f"Successfully retrieved {len(result)} cards from board {id_board} with filter '{filter}'"
    }


@mcp.tool(
    "TRELLO_GET_BOARDS_CARDS_BY_ID_BOARD",
    description="Get cards by board ID. Retrieves cards from an existing trello board, allowing filtering and customization of fields for cards, attachments, and members.",
)
def TRELLO_GET_BOARDS_CARDS_BY_ID_BOARD(
    id_board: Annotated[str, "The ID of the board to get cards from."],
    actions: Annotated[str, "Include actions in the response."] = "",
    attachment_fields: Annotated[str, "Comma-separated list of attachment fields. Defaults to all."] = "all",
    attachments: Annotated[str, "Include attachments."] = "",
    before: Annotated[str, "Return cards before this date."] = "",
    check_item_states: Annotated[str, "Include check item states."] = "",
    checklists: Annotated[str, "Include checklists. Defaults to none."] = "none",
    fields: Annotated[str, "Comma-separated list of card fields. Defaults to all."] = "all",
    filter: Annotated[str, "Filter cards. Defaults to visible."] = "visible",
    limit: Annotated[str, "Maximum number of cards to return."] = "",
    member_fields: Annotated[str, "Comma-separated list of member fields. Defaults to avatarHash, fullName, initials and username."] = "avatarHash,fullName,initials,username",
    members: Annotated[str, "Include members."] = "",
    since: Annotated[str, "Return cards since this date."] = "",
    stickers: Annotated[str, "Include stickers."] = ""
):
    """Get cards by board ID. Retrieves cards from an existing trello board, allowing filtering and customization of fields for cards, attachments, and members."""
    err = _validate_required({"id_board": id_board}, ["id_board"])
    if err:
        return err
    
    # Build the endpoint
    endpoint = f"/boards/{id_board}/cards"
    
    # Build query parameters
    params = {}
    
    # Add parameters only if they have values and are not defaults
    if actions and actions.strip():
        params["actions"] = actions.strip()
    if attachment_fields and attachment_fields.strip() and attachment_fields.lower() != "all":
        params["attachment_fields"] = attachment_fields.strip()
    if attachments and attachments.strip():
        params["attachments"] = attachments.strip()
    if before and before.strip():
        params["before"] = before.strip()
    if check_item_states and check_item_states.strip():
        params["checkItemStates"] = check_item_states.strip()
    if checklists and checklists.strip() and checklists.lower() != "none":
        params["checklists"] = checklists.strip()
    if fields and fields.strip() and fields.lower() != "all":
        params["fields"] = fields.strip()
    if filter and filter.strip() and filter.lower() != "visible":
        params["filter"] = filter.strip()
    if limit and limit.strip():
        params["limit"] = limit.strip()
    if member_fields and member_fields.strip() and member_fields != "avatarHash,fullName,initials,username":
        params["member_fields"] = member_fields.strip()
    if members and members.strip():
        params["members"] = members.strip()
    if since and since.strip():
        params["since"] = since.strip()
    if stickers and stickers.strip():
        params["stickers"] = stickers.strip()
    
    # Make the API request
    result = trello_request("GET", endpoint, params=params)
    
    if not isinstance(result, list):
        return {
            "successful": False,
            "error": "Invalid cards data received",
            "action": "get_cards_by_board",
            "board_id": id_board,
            "message": f"Failed to retrieve cards from board {id_board}"
        }
    
    return {
        "successful": True,
        "data": result,
        "action": "get_cards_by_board",
        "board_id": id_board,
        "card_count": len(result),
        "filter": filter,
        "fields": fields,
        "message": f"Successfully retrieved {len(result)} cards from board {id_board}"
    }


@mcp.tool(
    "TRELLO_GET_BOARDS_BY_ID_BOARD_BY_FIELD",
    description="Get board field. Retrieves the value of a single, specified field from a trello board.",
)
def TRELLO_GET_BOARDS_BY_ID_BOARD_BY_FIELD(
    id_board: Annotated[str, "The ID of the board to get the field from."],
    field: Annotated[str, "The specific field to retrieve from the board."]
):
    """Get board field. Retrieves the value of a single, specified field from a trello board."""
    err = _validate_required({"id_board": id_board, "field": field}, ["id_board", "field"])
    if err:
        return err
    
    # Handle "all" field to get all board data
    if field.lower() == "all":
        endpoint = f"/boards/{id_board}"
    else:
        endpoint = f"/boards/{id_board}/{field}"
    
    # Make the API request
    result = trello_request("GET", endpoint)
    
    if not isinstance(result, (dict, str, int, bool, list)):
        return {
            "successful": False,
            "error": "Invalid board field data received",
            "action": "get_board_field",
            "board_id": id_board,
            "field": field,
            "message": f"Failed to retrieve field '{field}' from board {id_board}"
        }
    
    return {
        "successful": True,
        "data": result,
        "action": "get_board_field",
        "board_id": id_board,
        "field": field,
        "message": f"Successfully retrieved field '{field}' from board {id_board}"
    }


@mcp.tool(
    "TRELLO_GET_BOARDS_BY_ID_BOARD",
    description="Get board by id. Fetches comprehensive details for a specific trello board by its id; this is a read-only action.",
)
def TRELLO_GET_BOARDS_BY_ID_BOARD(
    id_board: Annotated[str, "The ID of the board to get details from."],
    action_fields: Annotated[str, "Comma-separated list of action fields to return. Defaults to all."] = "all",
    action_member: Annotated[str, "Filter actions by member."] = "",
    action_member_creator: Annotated[str, "Filter actions by member creator."] = "",
    action_member_creator_fields: Annotated[str, "Comma-separated list of action member creator fields. Defaults to avatarHash, fullName, initials and username."] = "avatarHash,fullName,initials,username",
    action_member_fields: Annotated[str, "Comma-separated list of action member fields. Defaults to avatarHash, fullName, initials and username."] = "avatarHash,fullName,initials,username",
    actions: Annotated[str, "Include actions in the response."] = "",
    actions_display: Annotated[str, "Include display-friendly action representations."] = "",
    actions_entities: Annotated[str, "Include action entities."] = "",
    actions_format: Annotated[str, "Format of actions. Defaults to list."] = "list",
    actions_limit: Annotated[str, "Maximum number of actions to return. Defaults to 50."] = "50",
    actions_since: Annotated[str, "Return actions since this date."] = "",
    board_stars: Annotated[str, "Include board stars. Defaults to none."] = "none",
    card_attachment_fields: Annotated[str, "Comma-separated list of card attachment fields. Defaults to all."] = "all",
    card_attachments: Annotated[str, "Include card attachments."] = "",
    card_checklists: Annotated[str, "Include card checklists. Defaults to none."] = "none",
    card_fields: Annotated[str, "Comma-separated list of card fields. Defaults to all."] = "all",
    card_stickers: Annotated[str, "Include card stickers."] = "",
    cards: Annotated[str, "Include cards. Defaults to none."] = "none",
    checklist_fields: Annotated[str, "Comma-separated list of checklist fields. Defaults to all."] = "all",
    checklists: Annotated[str, "Include checklists. Defaults to none."] = "none",
    fields: Annotated[str, "Comma-separated list of board fields. Defaults to name, desc, descData, closed, idOrganization, pinned, url, shortUrl, prefs and labelNames."] = "name,desc,descData,closed,idOrganization,pinned,url,shortUrl,prefs,labelNames",
    label_fields: Annotated[str, "Comma-separated list of label fields. Defaults to all."] = "all",
    labels: Annotated[str, "Include labels. Defaults to none."] = "none",
    labels_limit: Annotated[str, "Maximum number of labels to return. Defaults to 50."] = "50",
    list_fields: Annotated[str, "Comma-separated list of list fields. Defaults to all."] = "all",
    lists: Annotated[str, "Include lists. Defaults to none."] = "none",
    member_fields: Annotated[str, "Comma-separated list of member fields. Defaults to avatarHash, initials, fullName, username and confirmed."] = "avatarHash,initials,fullName,username,confirmed",
    members: Annotated[str, "Include members. Defaults to none."] = "none",
    members_invited: Annotated[str, "Include invited members. Defaults to none."] = "none",
    members_invited_fields: Annotated[str, "Comma-separated list of invited member fields. Defaults to avatarHash, initials, fullName and username."] = "avatarHash,initials,fullName,username",
    memberships: Annotated[str, "Include memberships. Defaults to none."] = "none",
    memberships_member: Annotated[str, "Include membership member details."] = "",
    memberships_member_fields: Annotated[str, "Comma-separated list of membership member fields. Defaults to fullName and username."] = "fullName,username",
    my_prefs: Annotated[str, "Include user's board preferences."] = "",
    organization: Annotated[str, "Include organization details."] = "",
    organization_fields: Annotated[str, "Comma-separated list of organization fields. Defaults to name and displayName."] = "name,displayName",
    organization_memberships: Annotated[str, "Include organization memberships. Defaults to none."] = "none"
):
    """Get board by id. Fetches comprehensive details for a specific trello board by its id; this is a read-only action."""
    err = _validate_required({"id_board": id_board}, ["id_board"])
    if err:
        return err
    
    # Build the endpoint
    endpoint = f"/boards/{id_board}"
    
    # Build query parameters
    params = {}
    
    # Add parameters only if they have values and are not defaults
    if action_fields and action_fields.strip() and action_fields.lower() != "all":
        params["action_fields"] = action_fields.strip()
    if action_member and action_member.strip():
        params["action_member"] = action_member.strip()
    if action_member_creator and action_member_creator.strip():
        params["action_memberCreator"] = action_member_creator.strip()
    if action_member_creator_fields and action_member_creator_fields.strip() and action_member_creator_fields != "avatarHash,fullName,initials,username":
        params["action_memberCreator_fields"] = action_member_creator_fields.strip()
    if action_member_fields and action_member_fields.strip() and action_member_fields != "avatarHash,fullName,initials,username":
        params["action_member_fields"] = action_member_fields.strip()
    if actions and actions.strip():
        params["actions"] = actions.strip()
    if actions_display and actions_display.strip():
        params["actions_display"] = actions_display.strip()
    if actions_entities and actions_entities.strip():
        params["actions_entities"] = actions_entities.strip()
    if actions_format and actions_format.strip() and actions_format.lower() != "list":
        params["actions_format"] = actions_format.strip()
    if actions_limit and actions_limit.strip() and actions_limit != "50":
        params["actions_limit"] = actions_limit.strip()
    if actions_since and actions_since.strip():
        params["actions_since"] = actions_since.strip()
    if board_stars and board_stars.strip() and board_stars.lower() != "none":
        params["boardStars"] = board_stars.strip()
    if card_attachment_fields and card_attachment_fields.strip() and card_attachment_fields.lower() != "all":
        params["card_attachment_fields"] = card_attachment_fields.strip()
    if card_attachments and card_attachments.strip():
        params["card_attachments"] = card_attachments.strip()
    if card_checklists and card_checklists.strip() and card_checklists.lower() != "none":
        params["card_checklists"] = card_checklists.strip()
    if card_fields and card_fields.strip() and card_fields.lower() != "all":
        params["card_fields"] = card_fields.strip()
    if card_stickers and card_stickers.strip():
        params["card_stickers"] = card_stickers.strip()
    if cards and cards.strip() and cards.lower() != "none":
        params["cards"] = cards.strip()
    if checklist_fields and checklist_fields.strip() and checklist_fields.lower() != "all":
        params["checklist_fields"] = checklist_fields.strip()
    if checklists and checklists.strip() and checklists.lower() != "none":
        params["checklists"] = checklists.strip()
    if fields and fields.strip() and fields != "name,desc,descData,closed,idOrganization,pinned,url,shortUrl,prefs,labelNames":
        params["fields"] = fields.strip()
    if label_fields and label_fields.strip() and label_fields.lower() != "all":
        params["label_fields"] = label_fields.strip()
    if labels and labels.strip() and labels.lower() != "none":
        params["labels"] = labels.strip()
    if labels_limit and labels_limit.strip() and labels_limit != "50":
        params["labels_limit"] = labels_limit.strip()
    if list_fields and list_fields.strip() and list_fields.lower() != "all":
        params["list_fields"] = list_fields.strip()
    if lists and lists.strip() and lists.lower() != "none":
        params["lists"] = lists.strip()
    if member_fields and member_fields.strip() and member_fields != "avatarHash,initials,fullName,username,confirmed":
        params["member_fields"] = member_fields.strip()
    if members and members.strip() and members.lower() != "none":
        params["members"] = members.strip()
    if members_invited and members_invited.strip() and members_invited.lower() != "none":
        params["membersInvited"] = members_invited.strip()
    if members_invited_fields and members_invited_fields.strip() and members_invited_fields != "avatarHash,initials,fullName,username":
        params["membersInvited_fields"] = members_invited_fields.strip()
    if memberships and memberships.strip() and memberships.lower() != "none":
        params["memberships"] = memberships.strip()
    if memberships_member and memberships_member.strip():
        params["memberships_member"] = memberships_member.strip()
    if memberships_member_fields and memberships_member_fields.strip() and memberships_member_fields != "fullName,username":
        params["memberships_member_fields"] = memberships_member_fields.strip()
    if my_prefs and my_prefs.strip():
        params["myPrefs"] = my_prefs.strip()
    if organization and organization.strip():
        params["organization"] = organization.strip()
    if organization_fields and organization_fields.strip() and organization_fields != "name,displayName":
        params["organization_fields"] = organization_fields.strip()
    if organization_memberships and organization_memberships.strip() and organization_memberships.lower() != "none":
        params["organization_memberships"] = organization_memberships.strip()
    
    # Make the API request
    result = trello_request("GET", endpoint, params=params)
    
    if not isinstance(result, dict):
        return {
            "successful": False,
            "error": "Invalid board data received",
            "action": "get_board_by_id",
            "board_id": id_board,
            "message": f"Failed to retrieve board {id_board}"
        }
    
    return {
        "successful": True,
        "data": result,
        "action": "get_board_by_id",
        "board_id": id_board,
        "board_name": result.get("name"),
        "board_url": result.get("url"),
        "board_short_url": result.get("shortUrl"),
        "board_organization": result.get("idOrganization"),
        "board_closed": result.get("closed"),
        "board_pinned": result.get("pinned"),
        "fields": fields,
        "message": f"Successfully retrieved board {id_board}"
    }


@mcp.tool(
    "TRELLO_UPDATE_BOARDS_BY_ID_BOARD",
    description="Update board by ID. Updates attributes (e.g., name, description, status, preferences) of an existing trello board identified by `idboard`.",
)
def TRELLO_UPDATE_BOARDS_BY_ID_BOARD(
    id_board: Annotated[str, "The ID of the board to update."],
    closed: Annotated[str | None, "Whether the board should be closed/archived (true/false)."] = None,
    desc: Annotated[str | None, "The description of the board."] = None,
    id_board_source: Annotated[str | None, "The ID of a board to copy settings from."] = None,
    id_organization: Annotated[str | None, "The ID of the organization to move the board to."] = None,
    keep_from_source: Annotated[str | None, "What to keep from the source board when copying."] = None,
    label_names__blue: Annotated[str | None, "The name for the blue label."] = None,
    label_names__green: Annotated[str | None, "The name for the green label."] = None,
    label_names__orange: Annotated[str | None, "The name for the orange label."] = None,
    label_names__purple: Annotated[str | None, "The name for the purple label."] = None,
    label_names__red: Annotated[str | None, "The name for the red label."] = None,
    label_names__yellow: Annotated[str | None, "The name for the yellow label."] = None,
    name: Annotated[str | None, "The name of the board."] = None,
    power_ups: Annotated[str | None, "The power-ups to enable on the board."] = None,
    prefs__background: Annotated[str | None, "The background preference for the board."] = None,
    prefs__calendar_feed_enabled: Annotated[str | None, "Whether calendar feed is enabled (true/false)."] = None,
    prefs__card_aging: Annotated[str | None, "The card aging preference (pirate/regular)."] = None,
    prefs__card_covers: Annotated[str | None, "Whether card covers are enabled (true/false)."] = None,
    prefs__comments: Annotated[str | None, "Who can comment (members/observers/disabled)."] = None,
    prefs__invitations: Annotated[str | None, "Who can invite (members/admins)."] = None,
    prefs__permission_level: Annotated[str | None, "The permission level (private/org/public)."] = None,
    prefs__self_join: Annotated[str | None, "Whether members can join themselves (true/false)."] = None,
    prefs__voting: Annotated[str | None, "Who can vote (members/observers/disabled)."] = None,
    prefs_background: Annotated[str | None, "The background preference for the board (alternative format)."] = None,
    prefs_card_aging: Annotated[str | None, "The card aging preference (alternative format)."] = None,
    prefs_card_covers: Annotated[str | None, "Whether card covers are enabled (alternative format)."] = None,
    prefs_comments: Annotated[str | None, "Who can comment (alternative format)."] = None,
    prefs_invitations: Annotated[str | None, "Who can invite (alternative format)."] = None,
    prefs_permission_level: Annotated[str | None, "The permission level (alternative format)."] = None,
    prefs_self_join: Annotated[str | None, "Whether members can join themselves (alternative format)."] = None,
    prefs_voting: Annotated[str | None, "Who can vote (alternative format)."] = None,
    subscribed: Annotated[str | None, "Whether the user is subscribed to the board (true/false)."] = None
):
    """Update board by ID. Updates attributes (e.g., name, description, status, preferences) of an existing trello board identified by `idboard`."""
    err = _validate_required({"id_board": id_board}, ["id_board"])
    if err:
        return err
    
    try:
        endpoint = f"/boards/{id_board}"
        
        # Build data payload
        data = {}
        
        # Basic board attributes
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
        if name is not None:
            data["name"] = name
        if power_ups is not None:
            data["powerUps"] = power_ups
        if subscribed is not None:
            data["subscribed"] = subscribed
        
        # Label names
        label_names = {}
        if label_names__blue is not None:
            label_names["blue"] = label_names__blue
        if label_names__green is not None:
            label_names["green"] = label_names__green
        if label_names__orange is not None:
            label_names["orange"] = label_names__orange
        if label_names__purple is not None:
            label_names["purple"] = label_names__purple
        if label_names__red is not None:
            label_names["red"] = label_names__red
        if label_names__yellow is not None:
            label_names["yellow"] = label_names__yellow
        if label_names:
            data["labelNames"] = label_names
        
        # Board preferences
        prefs = {}
        if prefs__background is not None:
            prefs["background"] = prefs__background
        elif prefs_background is not None:
            prefs["background"] = prefs_background
        if prefs__calendar_feed_enabled is not None:
            prefs["calendarFeedEnabled"] = prefs__calendar_feed_enabled
        if prefs__card_aging is not None:
            prefs["cardAging"] = prefs__card_aging
        elif prefs_card_aging is not None:
            prefs["cardAging"] = prefs_card_aging
        if prefs__card_covers is not None:
            prefs["cardCovers"] = prefs__card_covers
        elif prefs_card_covers is not None:
            prefs["cardCovers"] = prefs_card_covers
        if prefs__comments is not None:
            prefs["comments"] = prefs__comments
        elif prefs_comments is not None:
            prefs["comments"] = prefs_comments
        if prefs__invitations is not None:
            prefs["invitations"] = prefs__invitations
        elif prefs_invitations is not None:
            prefs["invitations"] = prefs_invitations
        if prefs__permission_level is not None:
            prefs["permissionLevel"] = prefs__permission_level
        elif prefs_permission_level is not None:
            prefs["permissionLevel"] = prefs_permission_level
        if prefs__self_join is not None:
            prefs["selfJoin"] = prefs__self_join
        elif prefs_self_join is not None:
            prefs["selfJoin"] = prefs_self_join
        if prefs__voting is not None:
            prefs["voting"] = prefs__voting
        elif prefs_voting is not None:
            prefs["voting"] = prefs_voting
        if prefs:
            data["prefs"] = prefs
        
        # Make sure we have something to update
        if not data:
            return {
                "successful": False,
                "error": "No update parameters provided",
                "action": "update_board",
                "board_id": id_board,
                "message": "Must provide at least one parameter to update"
            }
        
        result = trello_request("PUT", endpoint, data=data)
        
        return {
            "successful": True,
            "data": result,
            "action": "update_board",
            "board_id": id_board,
            "updated_attributes": list(data.keys()),
            "message": f"Successfully updated board {id_board}"
        }
    except Exception as e:
        error_message = str(e)
        
        # Provide specific guidance for common errors
        if "403" in error_message:
            return {
                "successful": False,
                "error": f"Permission denied: {error_message}",
                "action": "update_board",
                "board_id": id_board,
                "message": f"Failed to update board {id_board} - insufficient permissions",
                "guidance": "You must be an admin of the board to update its settings.",
                "suggestion": "Verify you have admin access to the board or ask a board admin to make the change."
            }
        elif "404" in error_message:
            return {
                "successful": False,
                "error": f"Board not found: {error_message}",
                "action": "update_board",
                "board_id": id_board,
                "message": f"Failed to update board {id_board} - board not found",
                "guidance": "The board ID may be invalid or the board may have been deleted.",
                "suggestion": "Verify the board ID is correct and the board still exists."
            }
        elif "400" in error_message:
            return {
                "successful": False,
                "error": f"Invalid parameters: {error_message}",
                "action": "update_board",
                "board_id": id_board,
                "message": f"Failed to update board {id_board} - invalid parameters",
                "guidance": "Check that all provided parameters have valid values.",
                "suggestion": "Review the parameter values and ensure they match the expected format."
            }
        else:
            return {
                "successful": False,
                "error": f"Failed to update board: {error_message}",
                "action": "update_board",
                "board_id": id_board,
                "message": f"Failed to update board {id_board}"
            }


@mcp.tool(
    "TRELLO_UPDATE_BOARDS_CLOSED_BY_ID_BOARD",
    description="Update board closed status. Archives (closes) an active trello board or reopens a previously archived board.",
)
def TRELLO_UPDATE_BOARDS_CLOSED_BY_ID_BOARD(
    id_board: Annotated[str, "The ID of the board to archive or unarchive."],
    value: Annotated[str, "The closed status: 'true' to archive the board, 'false' to unarchive it."]
):
    """Update board closed status. Archives (closes) an active trello board or reopens a previously archived board."""
    err = _validate_required({"id_board": id_board, "value": value}, ["id_board", "value"])
    if err:
        return err
    
    try:
        endpoint = f"/boards/{id_board}"
        
        # Build data payload
        data = {
            "closed": value
        }
        
        result = trello_request("PUT", endpoint, data=data)
        
        # Determine the action taken
        action_taken = "archived" if value.lower() == "true" else "unarchived"
        
        return {
            "successful": True,
            "data": result,
            "action": "update_board_closed_status",
            "board_id": id_board,
            "closed_status": value,
            "action_taken": action_taken,
            "message": f"Successfully {action_taken} board {id_board}"
        }
    except Exception as e:
        error_message = str(e)
        
        # Provide specific guidance for common errors
        if "403" in error_message:
            return {
                "successful": False,
                "error": f"Permission denied: {error_message}",
                "action": "update_board_closed_status",
                "board_id": id_board,
                "message": f"Failed to update board closed status - insufficient permissions",
                "guidance": "You must be an admin of the board to archive or unarchive it.",
                "suggestion": "Verify you have admin access to the board or ask a board admin to make the change."
            }
        elif "404" in error_message:
            return {
                "successful": False,
                "error": f"Board not found: {error_message}",
                "action": "update_board_closed_status",
                "board_id": id_board,
                "message": f"Failed to update board closed status - board not found",
                "guidance": "The board ID may be invalid or the board may have been deleted.",
                "suggestion": "Verify the board ID is correct and the board still exists."
            }
        elif "400" in error_message and "value" in error_message.lower():
            return {
                "successful": False,
                "error": f"Invalid value: {error_message}",
                "action": "update_board_closed_status",
                "board_id": id_board,
                "message": f"Failed to update board closed status - invalid value '{value}'",
                "guidance": "The value must be 'true' to archive the board or 'false' to unarchive it.",
                "suggestion": "Use 'true' to archive the board or 'false' to unarchive it."
            }
        else:
            return {
                "successful": False,
                "error": f"Failed to update board closed status: {error_message}",
                "action": "update_board_closed_status",
                "board_id": id_board,
                "message": f"Failed to update board closed status for board {id_board}"
            }


@mcp.tool(
    "TRELLO_UPDATE_BOARDS_DESC_BY_ID_BOARD",
    description="Update board description. Updates the description of a specified trello board; the update is immediate and does not affect other board elements like lists, cards, or membership.",
)
def TRELLO_UPDATE_BOARDS_DESC_BY_ID_BOARD(
    id_board: Annotated[str, "The ID of the board to update the description for."],
    value: Annotated[str, "The new description text for the board."]
):
    """Update board description. Updates the description of a specified trello board; the update is immediate and does not affect other board elements like lists, cards, or membership."""
    err = _validate_required({"id_board": id_board, "value": value}, ["id_board", "value"])
    if err:
        return err
    
    try:
        endpoint = f"/boards/{id_board}"
        
        # Build data payload
        data = {
            "desc": value
        }
        
        result = trello_request("PUT", endpoint, data=data)
        
        return {
            "successful": True,
            "data": result,
            "action": "update_board_description",
            "board_id": id_board,
            "new_description": value,
            "message": f"Successfully updated description for board {id_board}"
        }
    except Exception as e:
        error_message = str(e)
        
        # Provide specific guidance for common errors
        if "403" in error_message:
            return {
                "successful": False,
                "error": f"Permission denied: {error_message}",
                "action": "update_board_description",
                "board_id": id_board,
                "message": f"Failed to update board description - insufficient permissions",
                "guidance": "You must be an admin of the board to update its description.",
                "suggestion": "Verify you have admin access to the board or ask a board admin to make the change."
            }
        elif "404" in error_message:
            return {
                "successful": False,
                "error": f"Board not found: {error_message}",
                "action": "update_board_description",
                "board_id": id_board,
                "message": f"Failed to update board description - board not found",
                "guidance": "The board ID may be invalid or the board may have been deleted.",
                "suggestion": "Verify the board ID is correct and the board still exists."
            }
        elif "400" in error_message:
            return {
                "successful": False,
                "error": f"Invalid description: {error_message}",
                "action": "update_board_description",
                "board_id": id_board,
                "message": f"Failed to update board description - invalid description",
                "guidance": "Check that the description value is valid and properly formatted.",
                "suggestion": "Ensure the description text is valid and doesn't contain any problematic characters."
            }
        else:
            return {
                "successful": False,
                "error": f"Failed to update board description: {error_message}",
                "action": "update_board_description",
                "board_id": id_board,
                "message": f"Failed to update board description for board {id_board}"
            }


@mcp.tool(
    "TRELLO_UPDATE_BOARD_SIDEBAR_ACTIONS_PREFS",
    description="Update board sidebar actions preferences. Updates the current user's preference for the visibility of sidebar board actions on a specific trello board.",
)
def TRELLO_UPDATE_BOARD_SIDEBAR_ACTIONS_PREFS(
    id_board: Annotated[str, "The ID of the board to update sidebar actions preferences for."],
    value: Annotated[str, "The preference value for sidebar actions visibility (e.g., 'true' to show, 'false' to hide)."]
):
    """Update board sidebar actions preferences. Updates the current user's preference for the visibility of sidebar board actions on a specific trello board."""
    err = _validate_required({"id_board": id_board, "value": value}, ["id_board", "value"])
    if err:
        return err
    
    try:
        endpoint = f"/boards/{id_board}/myPrefs/showSidebarBoardActions"
        
        # Build data payload
        data = {
            "value": value
        }
        
        result = trello_request("PUT", endpoint, data=data)
        
        # Determine the preference set
        preference_set = "show" if value.lower() == "true" else "hide"
        
        return {
            "successful": True,
            "data": result,
            "action": "update_board_sidebar_actions_prefs",
            "board_id": id_board,
            "preference_value": value,
            "preference_set": preference_set,
            "message": f"Successfully updated sidebar actions preference to {preference_set} for board {id_board}"
        }
    except Exception as e:
        error_message = str(e)
        
        # Provide specific guidance for common errors
        if "403" in error_message:
            return {
                "successful": False,
                "error": f"Permission denied: {error_message}",
                "action": "update_board_sidebar_actions_prefs",
                "board_id": id_board,
                "message": f"Failed to update sidebar actions preferences - insufficient permissions",
                "guidance": "You must be a member of the board to update your personal preferences.",
                "suggestion": "Verify you have access to the board or ask a board admin to add you as a member."
            }
        elif "404" in error_message:
            return {
                "successful": False,
                "error": f"Board not found: {error_message}",
                "action": "update_board_sidebar_actions_prefs",
                "board_id": id_board,
                "message": f"Failed to update sidebar actions preferences - board not found",
                "guidance": "The board ID may be invalid or the board may have been deleted.",
                "suggestion": "Verify the board ID is correct and the board still exists."
            }
        elif "400" in error_message and "value" in error_message.lower():
            return {
                "successful": False,
                "error": f"Invalid value: {error_message}",
                "action": "update_board_sidebar_actions_prefs",
                "board_id": id_board,
                "message": f"Failed to update sidebar actions preferences - invalid value '{value}'",
                "guidance": "The value must be 'true' to show sidebar actions or 'false' to hide them.",
                "suggestion": "Use 'true' to show sidebar actions or 'false' to hide them."
            }
        else:
            return {
                "successful": False,
                "error": f"Failed to update sidebar actions preferences: {error_message}",
                "action": "update_board_sidebar_actions_prefs",
                "board_id": id_board,
                "message": f"Failed to update sidebar actions preferences for board {id_board}"
            }


@mcp.tool(
    "TRELLO_UPDATE_BOARDS_ID_ORGANIZATION_BY_ID_BOARD",
    description="Update board organization. Moves an existing trello board to a specified, existing trello organization, which can affect the board's visibility and member access.",
)
def TRELLO_UPDATE_BOARDS_ID_ORGANIZATION_BY_ID_BOARD(
    id_board: Annotated[str, "The ID of the board to move to a different organization."],
    value: Annotated[str, "The ID of the organization to move the board to."]
):
    """Update board organization. Moves an existing trello board to a specified, existing trello organization, which can affect the board's visibility and member access."""
    err = _validate_required({"id_board": id_board, "value": value}, ["id_board", "value"])
    if err:
        return err
    
    try:
        endpoint = f"/boards/{id_board}"
        
        # Build data payload
        data = {
            "idOrganization": value
        }
        
        result = trello_request("PUT", endpoint, data=data)
        
        return {
            "successful": True,
            "data": result,
            "action": "update_board_organization",
            "board_id": id_board,
            "new_organization_id": value,
            "message": f"Successfully moved board {id_board} to organization {value}"
        }
    except Exception as e:
        error_message = str(e)
        
        # Provide specific guidance for common errors
        if "403" in error_message:
            return {
                "successful": False,
                "error": f"Permission denied: {error_message}",
                "action": "update_board_organization",
                "board_id": id_board,
                "message": f"Failed to move board to organization - insufficient permissions",
                "guidance": "You must be an admin of both the board and the target organization to move the board.",
                "suggestion": "Verify you have admin access to both the board and the target organization."
            }
        elif "404" in error_message:
            return {
                "successful": False,
                "error": f"Board or organization not found: {error_message}",
                "action": "update_board_organization",
                "board_id": id_board,
                "message": f"Failed to move board - board or organization not found",
                "guidance": "The board ID or organization ID may be invalid, or the board/organization may have been deleted.",
                "suggestion": "Verify both the board ID and organization ID are correct and still exist."
            }
        elif "400" in error_message and "organization" in error_message.lower():
            return {
                "successful": False,
                "error": f"Invalid organization: {error_message}",
                "action": "update_board_organization",
                "board_id": id_board,
                "message": f"Failed to move board - invalid organization ID '{value}'",
                "guidance": "The organization ID may be invalid or you may not have access to it.",
                "suggestion": "Verify the organization ID is correct and that you have access to the organization."
            }
        elif "409" in error_message:
            return {
                "successful": False,
                "error": f"Conflict: {error_message}",
                "action": "update_board_organization",
                "board_id": id_board,
                "message": f"Failed to move board - conflict with current state",
                "guidance": "The board may already be in the target organization or there may be a conflict with the move operation.",
                "suggestion": "Check if the board is already in the target organization or if there are any restrictions preventing the move."
            }
        else:
            return {
                "successful": False,
                "error": f"Failed to move board to organization: {error_message}",
                "action": "update_board_organization",
                "board_id": id_board,
                "message": f"Failed to move board {id_board} to organization {value}"
            }


@mcp.tool(
    "TRELLO_UPDATE_BOARDS_LABEL_NAMES_BLUE_BY_ID_BOARD",
    description="Update a board's blue label name. Sets the name of the blue label for a trello board.",
)
def TRELLO_UPDATE_BOARDS_LABEL_NAMES_BLUE_BY_ID_BOARD(
    id_board: Annotated[str, "The ID of the board to update the blue label name for."],
    value: Annotated[str, "The new name for the blue label."]
):
    """Update a board's blue label name. Sets the name of the blue label for a trello board."""
    err = _validate_required({"id_board": id_board, "value": value}, ["id_board", "value"])
    if err:
        return err
    
    try:
        endpoint = f"/boards/{id_board}"
        
        # Build data payload for label names
        data = {
            "labelNames": {
                "blue": value
            }
        }
        
        result = trello_request("PUT", endpoint, data=data)
        
        return {
            "successful": True,
            "data": result,
            "action": "update_board_blue_label_name",
            "board_id": id_board,
            "new_blue_label_name": value,
            "message": f"Successfully updated blue label name to '{value}' for board {id_board}"
        }
    except Exception as e:
        error_message = str(e)
        
        # Provide specific guidance for common errors
        if "403" in error_message:
            return {
                "successful": False,
                "error": f"Permission denied: {error_message}",
                "action": "update_board_blue_label_name",
                "board_id": id_board,
                "message": f"Failed to update blue label name - insufficient permissions",
                "guidance": "You must be an admin of the board to update label names.",
                "suggestion": "Verify you have admin access to the board or ask a board admin to make the change."
            }
        elif "404" in error_message:
            return {
                "successful": False,
                "error": f"Board not found: {error_message}",
                "action": "update_board_blue_label_name",
                "board_id": id_board,
                "message": f"Failed to update blue label name - board not found",
                "guidance": "The board ID may be invalid or the board may have been deleted.",
                "suggestion": "Verify the board ID is correct and the board still exists."
            }
        elif "409" in error_message and "closed" in error_message.lower():
            return {
                "successful": False,
                "error": f"Board is closed: {error_message}",
                "action": "update_board_blue_label_name",
                "board_id": id_board,
                "message": f"Failed to update blue label name - board is archived",
                "guidance": "Closed boards cannot be edited. You must unarchive the board first.",
                "suggestion": "Use TRELLO_UPDATE_BOARDS_CLOSED_BY_ID_BOARD to unarchive the board first."
            }
        elif "400" in error_message:
            return {
                "successful": False,
                "error": f"Invalid label name: {error_message}",
                "action": "update_board_blue_label_name",
                "board_id": id_board,
                "message": f"Failed to update blue label name - invalid name '{value}'",
                "guidance": "Check that the label name is valid and doesn't contain problematic characters.",
                "suggestion": "Ensure the label name is valid and follows Trello's naming conventions."
            }
        else:
            return {
                "successful": False,
                "error": f"Failed to update blue label name: {error_message}",
                "action": "update_board_blue_label_name",
                "board_id": id_board,
                "message": f"Failed to update blue label name for board {id_board}"
            }


@mcp.tool(
    "TRELLO_UPDATE_BOARDS_LABEL_NAMES_GREEN_BY_ID_BOARD",
    description="Update board's green label name. Updates the name of the green label for a specified trello board; this change is board-wide, affects all cards using this label, and does not change the label's color.",
)
def TRELLO_UPDATE_BOARDS_LABEL_NAMES_GREEN_BY_ID_BOARD(
    id_board: Annotated[str, "The ID of the board to update the green label name for."],
    value: Annotated[str, "The new name for the green label."]
):
    """Update board's green label name. Updates the name of the green label for a specified trello board; this change is board-wide, affects all cards using this label, and does not change the label's color."""
    err = _validate_required({"id_board": id_board, "value": value}, ["id_board", "value"])
    if err:
        return err
    
    try:
        endpoint = f"/boards/{id_board}"
        
        # Build data payload for label names
        data = {
            "labelNames": {
                "green": value
            }
        }
        
        result = trello_request("PUT", endpoint, data=data)
        
        return {
            "successful": True,
            "data": result,
            "action": "update_board_green_label_name",
            "board_id": id_board,
            "new_green_label_name": value,
            "message": f"Successfully updated green label name to '{value}' for board {id_board}"
        }
    except Exception as e:
        error_message = str(e)
        
        # Provide specific guidance for common errors
        if "403" in error_message:
            return {
                "successful": False,
                "error": f"Permission denied: {error_message}",
                "action": "update_board_green_label_name",
                "board_id": id_board,
                "message": f"Failed to update green label name - insufficient permissions",
                "guidance": "You must be an admin of the board to update label names.",
                "suggestion": "Verify you have admin access to the board or ask a board admin to make the change."
            }
        elif "404" in error_message:
            return {
                "successful": False,
                "error": f"Board not found: {error_message}",
                "action": "update_board_green_label_name",
                "board_id": id_board,
                "message": f"Failed to update green label name - board not found",
                "guidance": "The board ID may be invalid or the board may have been deleted.",
                "suggestion": "Verify the board ID is correct and the board still exists."
            }
        elif "409" in error_message and "closed" in error_message.lower():
            return {
                "successful": False,
                "error": f"Board is closed: {error_message}",
                "action": "update_board_green_label_name",
                "board_id": id_board,
                "message": f"Failed to update green label name - board is archived",
                "guidance": "Closed boards cannot be edited. You must unarchive the board first.",
                "suggestion": "Use TRELLO_UPDATE_BOARDS_CLOSED_BY_ID_BOARD to unarchive the board first."
            }
        elif "400" in error_message:
            return {
                "successful": False,
                "error": f"Invalid label name: {error_message}",
                "action": "update_board_green_label_name",
                "board_id": id_board,
                "message": f"Failed to update green label name - invalid name '{value}'",
                "guidance": "Check that the label name is valid and doesn't contain problematic characters.",
                "suggestion": "Ensure the label name is valid and follows Trello's naming conventions."
            }
        else:
            return {
                "successful": False,
                "error": f"Failed to update green label name: {error_message}",
                "action": "update_board_green_label_name",
                "board_id": id_board,
                "message": f"Failed to update green label name for board {id_board}"
            }


@mcp.tool(
    "TRELLO_UPDATE_BOARDS_LABEL_NAMES_ORANGE_BY_ID_BOARD",
    description="Update board label orange name. Updates the name of the orange label for a specified trello board, affecting only the label's name, not its color or associated cards.",
)
def TRELLO_UPDATE_BOARDS_LABEL_NAMES_ORANGE_BY_ID_BOARD(
    id_board: Annotated[str, "The ID of the board to update the orange label name for."],
    value: Annotated[str, "The new name for the orange label."]
):
    """Update board label orange name. Updates the name of the orange label for a specified trello board, affecting only the label's name, not its color or associated cards."""
    err = _validate_required({"id_board": id_board, "value": value}, ["id_board", "value"])
    if err:
        return err
    
    try:
        endpoint = f"/boards/{id_board}"
        
        # Build data payload for label names
        data = {
            "labelNames": {
                "orange": value
            }
        }
        
        result = trello_request("PUT", endpoint, data=data)
        
        return {
            "successful": True,
            "data": result,
            "action": "update_board_orange_label_name",
            "board_id": id_board,
            "new_orange_label_name": value,
            "message": f"Successfully updated orange label name to '{value}' for board {id_board}"
        }
    except Exception as e:
        error_message = str(e)
        
        # Provide specific guidance for common errors
        if "403" in error_message:
            return {
                "successful": False,
                "error": f"Permission denied: {error_message}",
                "action": "update_board_orange_label_name",
                "board_id": id_board,
                "message": f"Failed to update orange label name - insufficient permissions",
                "guidance": "You must be an admin of the board to update label names.",
                "suggestion": "Verify you have admin access to the board or ask a board admin to make the change."
            }
        elif "404" in error_message:
            return {
                "successful": False,
                "error": f"Board not found: {error_message}",
                "action": "update_board_orange_label_name",
                "board_id": id_board,
                "message": f"Failed to update orange label name - board not found",
                "guidance": "The board ID may be invalid or the board may have been deleted.",
                "suggestion": "Verify the board ID is correct and the board still exists."
            }
        elif "409" in error_message and "closed" in error_message.lower():
            return {
                "successful": False,
                "error": f"Board is closed: {error_message}",
                "action": "update_board_orange_label_name",
                "board_id": id_board,
                "message": f"Failed to update orange label name - board is archived",
                "guidance": "Closed boards cannot be edited. You must unarchive the board first.",
                "suggestion": "Use TRELLO_UPDATE_BOARDS_CLOSED_BY_ID_BOARD to unarchive the board first."
            }
        elif "400" in error_message:
            return {
                "successful": False,
                "error": f"Invalid label name: {error_message}",
                "action": "update_board_orange_label_name",
                "board_id": id_board,
                "message": f"Failed to update orange label name - invalid name '{value}'",
                "guidance": "Check that the label name is valid and doesn't contain problematic characters.",
                "suggestion": "Ensure the label name is valid and follows Trello's naming conventions."
            }
        else:
            return {
                "successful": False,
                "error": f"Failed to update orange label name: {error_message}",
                "action": "update_board_orange_label_name",
                "board_id": id_board,
                "message": f"Failed to update orange label name for board {id_board}"
            }


@mcp.tool(
    "TRELLO_UPDATE_BOARDS_LABEL_NAMES_PURPLE_BY_ID_BOARD",
    description="Update purple label name. Updates the name of the purple label on a trello board specified by `idboard`.",
)
def TRELLO_UPDATE_BOARDS_LABEL_NAMES_PURPLE_BY_ID_BOARD(
    id_board: Annotated[str, "The ID of the board to update the purple label name for."],
    value: Annotated[str, "The new name for the purple label."]
):
    """Update purple label name. Updates the name of the purple label on a trello board specified by `idboard`."""
    err = _validate_required({"id_board": id_board, "value": value}, ["id_board", "value"])
    if err:
        return err
    
    try:
        endpoint = f"/boards/{id_board}"
        
        # Build data payload for label names
        data = {
            "labelNames": {
                "purple": value
            }
        }
        
        result = trello_request("PUT", endpoint, data=data)
        
        return {
            "successful": True,
            "data": result,
            "action": "update_board_purple_label_name",
            "board_id": id_board,
            "new_purple_label_name": value,
            "message": f"Successfully updated purple label name to '{value}' for board {id_board}"
        }
    except Exception as e:
        error_message = str(e)
        
        # Provide specific guidance for common errors
        if "403" in error_message:
            return {
                "successful": False,
                "error": f"Permission denied: {error_message}",
                "action": "update_board_purple_label_name",
                "board_id": id_board,
                "message": f"Failed to update purple label name - insufficient permissions",
                "guidance": "You must be an admin of the board to update label names.",
                "suggestion": "Verify you have admin access to the board or ask a board admin to make the change."
            }
        elif "404" in error_message:
            return {
                "successful": False,
                "error": f"Board not found: {error_message}",
                "action": "update_board_purple_label_name",
                "board_id": id_board,
                "message": f"Failed to update purple label name - board not found",
                "guidance": "The board ID may be invalid or the board may have been deleted.",
                "suggestion": "Verify the board ID is correct and the board still exists."
            }
        elif "409" in error_message and "closed" in error_message.lower():
            return {
                "successful": False,
                "error": f"Board is closed: {error_message}",
                "action": "update_board_purple_label_name",
                "board_id": id_board,
                "message": f"Failed to update purple label name - board is archived",
                "guidance": "Closed boards cannot be edited. You must unarchive the board first.",
                "suggestion": "Use TRELLO_UPDATE_BOARDS_CLOSED_BY_ID_BOARD to unarchive the board first."
            }
        elif "400" in error_message:
            return {
                "successful": False,
                "error": f"Invalid label name: {error_message}",
                "action": "update_board_purple_label_name",
                "board_id": id_board,
                "message": f"Failed to update purple label name - invalid name '{value}'",
                "guidance": "Check that the label name is valid and doesn't contain problematic characters.",
                "suggestion": "Ensure the label name is valid and follows Trello's naming conventions."
            }
        else:
            return {
                "successful": False,
                "error": f"Failed to update purple label name: {error_message}",
                "action": "update_board_purple_label_name",
                "board_id": id_board,
                "message": f"Failed to update purple label name for board {id_board}"
            }


@mcp.tool(
    "TRELLO_UPDATE_BOARDS_LABEL_NAMES_RED_BY_ID_BOARD",
    description="Update board label name red. Updates the name of the red label on a specified trello board, without affecting its color or other labels.",
)
def TRELLO_UPDATE_BOARDS_LABEL_NAMES_RED_BY_ID_BOARD(
    id_board: Annotated[str, "The ID of the board to update the red label name for."],
    value: Annotated[str, "The new name for the red label."]
):
    """Update board label name red. Updates the name of the red label on a specified trello board, without affecting its color or other labels."""
    err = _validate_required({"id_board": id_board, "value": value}, ["id_board", "value"])
    if err:
        return err
    
    try:
        endpoint = f"/boards/{id_board}"
        
        # Build data payload for label names
        data = {
            "labelNames": {
                "red": value
            }
        }
        
        result = trello_request("PUT", endpoint, data=data)
        
        return {
            "successful": True,
            "data": result,
            "action": "update_board_red_label_name",
            "board_id": id_board,
            "new_red_label_name": value,
            "message": f"Successfully updated red label name to '{value}' for board {id_board}"
        }
    except Exception as e:
        error_message = str(e)
        
        # Provide specific guidance for common errors
        if "403" in error_message:
            return {
                "successful": False,
                "error": f"Permission denied: {error_message}",
                "action": "update_board_red_label_name",
                "board_id": id_board,
                "message": f"Failed to update red label name - insufficient permissions",
                "guidance": "You must be an admin of the board to update label names.",
                "suggestion": "Verify you have admin access to the board or ask a board admin to make the change."
            }
        elif "404" in error_message:
            return {
                "successful": False,
                "error": f"Board not found: {error_message}",
                "action": "update_board_red_label_name",
                "board_id": id_board,
                "message": f"Failed to update red label name - board not found",
                "guidance": "The board ID may be invalid or the board may have been deleted.",
                "suggestion": "Verify the board ID is correct and the board still exists."
            }
        elif "409" in error_message and "closed" in error_message.lower():
            return {
                "successful": False,
                "error": f"Board is closed: {error_message}",
                "action": "update_board_red_label_name",
                "board_id": id_board,
                "message": f"Failed to update red label name - board is archived",
                "guidance": "Closed boards cannot be edited. You must unarchive the board first.",
                "suggestion": "Use TRELLO_UPDATE_BOARDS_CLOSED_BY_ID_BOARD to unarchive the board first."
            }
        elif "400" in error_message:
            return {
                "successful": False,
                "error": f"Invalid label name: {error_message}",
                "action": "update_board_red_label_name",
                "board_id": id_board,
                "message": f"Failed to update red label name - invalid name '{value}'",
                "guidance": "Check that the label name is valid and doesn't contain problematic characters.",
                "suggestion": "Ensure the label name is valid and follows Trello's naming conventions."
            }
        else:
            return {
                "successful": False,
                "error": f"Failed to update red label name: {error_message}",
                "action": "update_board_red_label_name",
                "board_id": id_board,
                "message": f"Failed to update red label name for board {id_board}"
            }


@mcp.tool(
    "TRELLO_UPDATE_BOARDS_LABEL_NAMES_YELLOW_BY_ID_BOARD",
    description="Update yellow label name on board. Updates the name of a board's yellow label; other colored labels are unaffected.",
)
def TRELLO_UPDATE_BOARDS_LABEL_NAMES_YELLOW_BY_ID_BOARD(
    id_board: Annotated[str, "The ID of the board to update the yellow label name for."],
    value: Annotated[str, "The new name for the yellow label."]
):
    """Update yellow label name on board. Updates the name of a board's yellow label; other colored labels are unaffected."""
    err = _validate_required({"id_board": id_board, "value": value}, ["id_board", "value"])
    if err:
        return err
    
    try:
        endpoint = f"/boards/{id_board}"
        
        # Build data payload for label names
        data = {
            "labelNames": {
                "yellow": value
            }
        }
        
        result = trello_request("PUT", endpoint, data=data)
        
        return {
            "successful": True,
            "data": result,
            "action": "update_board_yellow_label_name",
            "board_id": id_board,
            "new_yellow_label_name": value,
            "message": f"Successfully updated yellow label name to '{value}' for board {id_board}"
        }
    except Exception as e:
        error_message = str(e)
        
        # Provide specific guidance for common errors
        if "403" in error_message:
            return {
                "successful": False,
                "error": f"Permission denied: {error_message}",
                "action": "update_board_yellow_label_name",
                "board_id": id_board,
                "message": f"Failed to update yellow label name - insufficient permissions",
                "guidance": "You must be an admin of the board to update label names.",
                "suggestion": "Verify you have admin access to the board or ask a board admin to make the change."
            }
        elif "404" in error_message:
            return {
                "successful": False,
                "error": f"Board not found: {error_message}",
                "action": "update_board_yellow_label_name",
                "board_id": id_board,
                "message": f"Failed to update yellow label name - board not found",
                "guidance": "The board ID may be invalid or the board may have been deleted.",
                "suggestion": "Verify the board ID is correct and the board still exists."
            }
        elif "409" in error_message and "closed" in error_message.lower():
            return {
                "successful": False,
                "error": f"Board is closed: {error_message}",
                "action": "update_board_yellow_label_name",
                "board_id": id_board,
                "message": f"Failed to update yellow label name - board is archived",
                "guidance": "Closed boards cannot be edited. You must unarchive the board first.",
                "suggestion": "Use TRELLO_UPDATE_BOARDS_CLOSED_BY_ID_BOARD to unarchive the board first."
            }
        elif "400" in error_message:
            return {
                "successful": False,
                "error": f"Invalid label name: {error_message}",
                "action": "update_board_yellow_label_name",
                "board_id": id_board,
                "message": f"Failed to update yellow label name - invalid name '{value}'",
                "guidance": "Check that the label name is valid and doesn't contain problematic characters.",
                "suggestion": "Ensure the label name is valid and follows Trello's naming conventions."
            }
        else:
            return {
                "successful": False,
                "error": f"Failed to update yellow label name: {error_message}",
                "action": "update_board_yellow_label_name",
                "board_id": id_board,
                "message": f"Failed to update yellow label name for board {id_board}"
            }


@mcp.tool(
    "TRELLO_UPDATE_BOARDS_MEMBERS_BY_ID_BOARD",
    description="Update board members. Adds or updates a member's role on a specific trello board, typically requiring the member's `email` and a membership `type`.",
)
def TRELLO_UPDATE_BOARDS_MEMBERS_BY_ID_BOARD(
    id_board: Annotated[str, "The ID of the board to add or update the member on."],
    email: Annotated[str | None, "The email address of the member to add or update."] = None,
    full_name: Annotated[str | None, "The full name of the member to add or update."] = None,
    type: Annotated[str | None, "The membership type (e.g., 'admin', 'normal', 'observer')."] = None
):
    """Update board members. Adds or updates a member's role on a specific trello board, typically requiring the member's `email` and a membership `type`."""
    err = _validate_required({"id_board": id_board}, ["id_board"])
    if err:
        return err
    
    # Validate that at least email or fullName is provided
    if not email and not full_name:
        return {
            "successful": False,
            "error": "Missing required parameters",
            "action": "update_board_members",
            "board_id": id_board,
            "message": "Must provide either email or fullName to identify the member",
            "guidance": "You must provide either the member's email address or full name to add or update them.",
            "suggestion": "Provide either 'email' or 'fullName' parameter to identify the member."
        }
    
    try:
        endpoint = f"/boards/{id_board}/members"
        
        # Build data payload
        data = {}
        if email is not None:
            data["email"] = email
        if full_name is not None:
            data["fullName"] = full_name
        if type is not None:
            data["type"] = type
        
        result = trello_request("PUT", endpoint, data=data)
        
        return {
            "successful": True,
            "data": result,
            "action": "update_board_members",
            "board_id": id_board,
            "member_email": email,
            "member_full_name": full_name,
            "membership_type": type,
            "message": f"Successfully updated member on board {id_board}"
        }
    except Exception as e:
        error_message = str(e)
        
        # Provide specific guidance for common errors
        if "403" in error_message and "already invited" in error_message.lower():
            return {
                "successful": False,
                "error": f"Member already invited: {error_message}",
                "action": "update_board_members",
                "board_id": id_board,
                "message": f"Failed to add member - member is already on the board",
                "guidance": "The member you're trying to add is already a member of this board.",
                "suggestion": "Use TRELLO_UPDATE_BOARD_MEMBERSHIP to update the member's role instead, or check if the member is already on the board."
            }
        elif "403" in error_message:
            return {
                "successful": False,
                "error": f"Permission denied: {error_message}",
                "action": "update_board_members",
                "board_id": id_board,
                "message": f"Failed to update board members - insufficient permissions",
                "guidance": "You must be an admin of the board to add or update members.",
                "suggestion": "Verify you have admin access to the board or ask a board admin to make the change."
            }
        elif "404" in error_message:
            return {
                "successful": False,
                "error": f"Board or member not found: {error_message}",
                "action": "update_board_members",
                "board_id": id_board,
                "message": f"Failed to update board members - board or member not found",
                "guidance": "The board ID may be invalid, or the member may not exist or have access to the board.",
                "suggestion": "Verify the board ID is correct and the member exists in Trello."
            }
        elif "400" in error_message and "email" in error_message.lower():
            return {
                "successful": False,
                "error": f"Invalid email: {error_message}",
                "action": "update_board_members",
                "board_id": id_board,
                "message": f"Failed to update board members - invalid email '{email}'",
                "guidance": "The email address may be invalid or not associated with a Trello account.",
                "suggestion": "Verify the email address is correct and the person has a Trello account."
            }
        elif "400" in error_message and "type" in error_message.lower():
            return {
                "successful": False,
                "error": f"Invalid membership type: {error_message}",
                "action": "update_board_members",
                "board_id": id_board,
                "message": f"Failed to update board members - invalid type '{type}'",
                "guidance": "Valid membership types are: admin, normal, observer.",
                "suggestion": "Use one of the valid membership types: admin, normal, or observer."
            }
        elif "409" in error_message and "closed" in error_message.lower():
            return {
                "successful": False,
                "error": f"Board is closed: {error_message}",
                "action": "update_board_members",
                "board_id": id_board,
                "message": f"Failed to update board members - board is archived",
                "guidance": "Closed boards cannot be edited. You must unarchive the board first.",
                "suggestion": "Use TRELLO_UPDATE_BOARDS_CLOSED_BY_ID_BOARD to unarchive the board first."
            }
        else:
            return {
                "successful": False,
                "error": f"Failed to update board members: {error_message}",
                "action": "update_board_members",
                "board_id": id_board,
                "message": f"Failed to update board members for board {id_board}"
            }


@mcp.tool(
    "TRELLO_UPDATE_BOARDS_MEMBERS_BY_ID_BOARD_BY_ID_MEMBER",
    description="Update board member attributes. Updates a current member's email, full name, or role (admin, normal, or observer) on a specific trello board; email and full name changes are board-specific and do not affect the member's global trello profile.",
)
def TRELLO_UPDATE_BOARDS_MEMBERS_BY_ID_BOARD_BY_ID_MEMBER(
    id_board: Annotated[str, "The ID of the board containing the member."],
    id_member: Annotated[str, "The ID of the member to update."],
    email: Annotated[str | None, "The new email address for the member on this board."] = None,
    full_name: Annotated[str | None, "The new full name for the member on this board."] = None,
    type: Annotated[str | None, "The new membership type (e.g., 'admin', 'normal', 'observer')."] = None
):
    """Update board member attributes. Updates a current member's email, full name, or role (admin, normal, or observer) on a specific trello board; email and full name changes are board-specific and do not affect the member's global trello profile."""
    err = _validate_required({"id_board": id_board, "id_member": id_member}, ["id_board", "id_member"])
    if err:
        return err
    
    # Validate that at least one attribute is provided for update
    if not email and not full_name and not type:
        return {
            "successful": False,
            "error": "No update parameters provided",
            "action": "update_board_member_attributes",
            "board_id": id_board,
            "member_id": id_member,
            "message": "Must provide at least one parameter to update (email, fullName, or type)",
            "guidance": "You must provide at least one attribute to update: email, fullName, or type.",
            "suggestion": "Provide at least one of: email, fullName, or type to update the member's attributes."
        }
    
    try:
        endpoint = f"/boards/{id_board}/members/{id_member}"
        
        # Build data payload
        data = {}
        if email is not None:
            data["email"] = email
        if full_name is not None:
            data["fullName"] = full_name
        if type is not None:
            data["type"] = type
        
        result = trello_request("PUT", endpoint, data=data)
        
        return {
            "successful": True,
            "data": result,
            "action": "update_board_member_attributes",
            "board_id": id_board,
            "member_id": id_member,
            "updated_email": email,
            "updated_full_name": full_name,
            "updated_type": type,
            "message": f"Successfully updated member {id_member} attributes on board {id_board}"
        }
    except Exception as e:
        error_message = str(e)
        
        # Provide specific guidance for common errors
        if "403" in error_message:
            return {
                "successful": False,
                "error": f"Permission denied: {error_message}",
                "action": "update_board_member_attributes",
                "board_id": id_board,
                "member_id": id_member,
                "message": f"Failed to update member attributes - insufficient permissions",
                "guidance": "You must be an admin of the board to update member attributes.",
                "suggestion": "Verify you have admin access to the board or ask a board admin to make the change."
            }
        elif "404" in error_message:
            return {
                "successful": False,
                "error": f"Board or member not found: {error_message}",
                "action": "update_board_member_attributes",
                "board_id": id_board,
                "member_id": id_member,
                "message": f"Failed to update member attributes - board or member not found",
                "guidance": "The board ID or member ID may be invalid, or the member may not be on the board.",
                "suggestion": "Verify both the board ID and member ID are correct and the member is on the board."
            }
        elif "400" in error_message and "email" in error_message.lower():
            return {
                "successful": False,
                "error": f"Invalid email: {error_message}",
                "action": "update_board_member_attributes",
                "board_id": id_board,
                "member_id": id_member,
                "message": f"Failed to update member attributes - invalid email '{email}'",
                "guidance": "The email address may be invalid or already in use by another member.",
                "suggestion": "Verify the email address is valid and not already used by another board member."
            }
        elif "400" in error_message and "type" in error_message.lower():
            return {
                "successful": False,
                "error": f"Invalid membership type: {error_message}",
                "action": "update_board_member_attributes",
                "board_id": id_board,
                "member_id": id_member,
                "message": f"Failed to update member attributes - invalid type '{type}'",
                "guidance": "Valid membership types are: admin, normal, observer.",
                "suggestion": "Use one of the valid membership types: admin, normal, or observer."
            }
        elif "409" in error_message and "closed" in error_message.lower():
            return {
                "successful": False,
                "error": f"Board is closed: {error_message}",
                "action": "update_board_member_attributes",
                "board_id": id_board,
                "member_id": id_member,
                "message": f"Failed to update member attributes - board is archived",
                "guidance": "Closed boards cannot be edited. You must unarchive the board first.",
                "suggestion": "Use TRELLO_UPDATE_BOARDS_CLOSED_BY_ID_BOARD to unarchive the board first."
            }
        else:
            return {
                "successful": False,
                "error": f"Failed to update member attributes: {error_message}",
                "action": "update_board_member_attributes",
                "board_id": id_board,
                "member_id": id_member,
                "message": f"Failed to update member {id_member} attributes on board {id_board}"
            }


@mcp.tool(
    "TRELLO_UPDATE_BOARDS_MY_PREFS_EMAIL_POSITION_BY_ID_BOARD",
    description="Modify board email position preference. Updates a trello board's email position preference for new cards; this preference only affects new cards (not existing ones) and the board must exist.",
)
def TRELLO_UPDATE_BOARDS_MY_PREFS_EMAIL_POSITION_BY_ID_BOARD(
    id_board: Annotated[str, "The ID of the board to update email position preference for."],
    value: Annotated[str, "The email position preference value (e.g., 'top', 'bottom')."]
):
    """Modify board email position preference. Updates a trello board's email position preference for new cards; this preference only affects new cards (not existing ones) and the board must exist."""
    err = _validate_required({"id_board": id_board, "value": value}, ["id_board", "value"])
    if err:
        return err
    
    try:
        endpoint = f"/boards/{id_board}/myPrefs/emailPosition"
        
        # Build data payload
        data = {
            "value": value
        }
        
        result = trello_request("PUT", endpoint, data=data)
        
        return {
            "successful": True,
            "data": result,
            "action": "update_board_email_position_preference",
            "board_id": id_board,
            "email_position_preference": value,
            "message": f"Successfully updated email position preference to '{value}' for board {id_board}"
        }
    except Exception as e:
        error_message = str(e)
        
        # Provide specific guidance for common errors
        if "403" in error_message:
            return {
                "successful": False,
                "error": f"Permission denied: {error_message}",
                "action": "update_board_email_position_preference",
                "board_id": id_board,
                "message": f"Failed to update email position preference - insufficient permissions",
                "guidance": "You must be a member of the board to update your personal preferences.",
                "suggestion": "Verify you have access to the board or ask a board admin to add you as a member."
            }
        elif "404" in error_message:
            return {
                "successful": False,
                "error": f"Board not found: {error_message}",
                "action": "update_board_email_position_preference",
                "board_id": id_board,
                "message": f"Failed to update email position preference - board not found",
                "guidance": "The board ID may be invalid or the board may have been deleted.",
                "suggestion": "Verify the board ID is correct and the board still exists."
            }
        elif "400" in error_message and "value" in error_message.lower():
            return {
                "successful": False,
                "error": f"Invalid email position value: {error_message}",
                "action": "update_board_email_position_preference",
                "board_id": id_board,
                "message": f"Failed to update email position preference - invalid value '{value}'",
                "guidance": "Valid email position values are typically 'top' or 'bottom'.",
                "suggestion": "Use 'top' to place new cards at the top of lists, or 'bottom' to place them at the bottom."
            }
        elif "409" in error_message and "closed" in error_message.lower():
            return {
                "successful": False,
                "error": f"Board is closed: {error_message}",
                "action": "update_board_email_position_preference",
                "board_id": id_board,
                "message": f"Failed to update email position preference - board is archived",
                "guidance": "Closed boards cannot be edited. You must unarchive the board first.",
                "suggestion": "Use TRELLO_UPDATE_BOARDS_CLOSED_BY_ID_BOARD to unarchive the board first."
            }
        else:
            return {
                "successful": False,
                "error": f"Failed to update email position preference: {error_message}",
                "action": "update_board_email_position_preference",
                "board_id": id_board,
                "message": f"Failed to update email position preference for board {id_board}"
            }


@mcp.tool(
    "TRELLO_UPDATE_BOARDS_MY_PREFS_ID_EMAIL_LIST_BY_ID_BOARD",
    description="Update board email list preference. Sets or disables the default trello list for new cards created via email on a specific board.",
)
def TRELLO_UPDATE_BOARDS_MY_PREFS_ID_EMAIL_LIST_BY_ID_BOARD(
    id_board: Annotated[str, "The ID of the board to update email list preference for."],
    value: Annotated[str, "The list ID to set as default for email cards, or 'none' to disable the preference."]
):
    """Update board email list preference. Sets or disables the default trello list for new cards created via email on a specific board."""
    err = _validate_required({"id_board": id_board, "value": value}, ["id_board", "value"])
    if err:
        return err
    
    try:
        endpoint = f"/boards/{id_board}/myPrefs/idEmailList"
        
        # Build data payload
        data = {
            "value": value
        }
        
        result = trello_request("PUT", endpoint, data=data)
        
        # Determine the action taken
        action_taken = "disabled" if value.lower() == "none" else "set"
        list_info = "disabled" if value.lower() == "none" else f"list {value}"
        
        return {
            "successful": True,
            "data": result,
            "action": "update_board_email_list_preference",
            "board_id": id_board,
            "email_list_preference": value,
            "action_taken": action_taken,
            "list_info": list_info,
            "message": f"Successfully {action_taken} email list preference to '{value}' for board {id_board}"
        }
    except Exception as e:
        error_message = str(e)
        
        # Provide specific guidance for common errors
        if "403" in error_message:
            return {
                "successful": False,
                "error": f"Permission denied: {error_message}",
                "action": "update_board_email_list_preference",
                "board_id": id_board,
                "message": f"Failed to update email list preference - insufficient permissions",
                "guidance": "You must be a member of the board to update your personal preferences.",
                "suggestion": "Verify you have access to the board or ask a board admin to add you as a member."
            }
        elif "404" in error_message:
            return {
                "successful": False,
                "error": f"Board or list not found: {error_message}",
                "action": "update_board_email_list_preference",
                "board_id": id_board,
                "message": f"Failed to update email list preference - board or list not found",
                "guidance": "The board ID may be invalid, or the list ID may not exist on this board.",
                "suggestion": "Verify the board ID is correct and the list ID exists on the board."
            }
        elif "400" in error_message and "value" in error_message.lower():
            return {
                "successful": False,
                "error": f"Invalid list ID: {error_message}",
                "action": "update_board_email_list_preference",
                "board_id": id_board,
                "message": f"Failed to update email list preference - invalid list ID '{value}'",
                "guidance": "The list ID may be invalid or not accessible on this board.",
                "suggestion": "Use a valid list ID from the board, or 'none' to disable the preference."
            }
        elif "409" in error_message and "closed" in error_message.lower():
            return {
                "successful": False,
                "error": f"Board is closed: {error_message}",
                "action": "update_board_email_list_preference",
                "board_id": id_board,
                "message": f"Failed to update email list preference - board is archived",
                "guidance": "Closed boards cannot be edited. You must unarchive the board first.",
                "suggestion": "Use TRELLO_UPDATE_BOARDS_CLOSED_BY_ID_BOARD to unarchive the board first."
            }
        else:
            return {
                "successful": False,
                "error": f"Failed to update email list preference: {error_message}",
                "action": "update_board_email_list_preference",
                "board_id": id_board,
                "message": f"Failed to update email list preference for board {id_board}"
            }


@mcp.tool(
    "TRELLO_UPDATE_BOARDS_MY_PREFS_SHOW_SIDEBAR_ACTIVITY_BY_ID_BOARD",
    description="Update my board sidebar activity preference. Sets the current user's preference for displaying or concealing the sidebar activity feed on an accessible trello board; this change only affects the requesting user.",
)
def TRELLO_UPDATE_BOARDS_MY_PREFS_SHOW_SIDEBAR_ACTIVITY_BY_ID_BOARD(
    id_board: Annotated[str, "The ID of the board to update sidebar activity preference for."],
    value: Annotated[str, "The sidebar activity preference value (e.g., 'true' to show, 'false' to hide)."]
):
    """Update my board sidebar activity preference. Sets the current user's preference for displaying or concealing the sidebar activity feed on an accessible trello board; this change only affects the requesting user."""
    err = _validate_required({"id_board": id_board, "value": value}, ["id_board", "value"])
    if err:
        return err
    
    try:
        endpoint = f"/boards/{id_board}/myPrefs/showSidebarActivity"
        
        # Build data payload
        data = {
            "value": value
        }
        
        result = trello_request("PUT", endpoint, data=data)
        
        # Determine the preference set
        preference_set = "show" if value.lower() == "true" else "hide"
        
        return {
            "successful": True,
            "data": result,
            "action": "update_board_sidebar_activity_preference",
            "board_id": id_board,
            "sidebar_activity_preference": value,
            "preference_set": preference_set,
            "message": f"Successfully updated sidebar activity preference to {preference_set} for board {id_board}"
        }
    except Exception as e:
        error_message = str(e)
        
        # Provide specific guidance for common errors
        if "403" in error_message:
            return {
                "successful": False,
                "error": f"Permission denied: {error_message}",
                "action": "update_board_sidebar_activity_preference",
                "board_id": id_board,
                "message": f"Failed to update sidebar activity preference - insufficient permissions",
                "guidance": "You must be a member of the board to update your personal preferences.",
                "suggestion": "Verify you have access to the board or ask a board admin to add you as a member."
            }
        elif "404" in error_message:
            return {
                "successful": False,
                "error": f"Board not found: {error_message}",
                "action": "update_board_sidebar_activity_preference",
                "board_id": id_board,
                "message": f"Failed to update sidebar activity preference - board not found",
                "guidance": "The board ID may be invalid or the board may have been deleted.",
                "suggestion": "Verify the board ID is correct and the board still exists."
            }
        elif "400" in error_message and "value" in error_message.lower():
            return {
                "successful": False,
                "error": f"Invalid preference value: {error_message}",
                "action": "update_board_sidebar_activity_preference",
                "board_id": id_board,
                "message": f"Failed to update sidebar activity preference - invalid value '{value}'",
                "guidance": "Valid preference values are 'true' to show the sidebar activity or 'false' to hide it.",
                "suggestion": "Use 'true' to show the sidebar activity or 'false' to hide it."
            }
        elif "410" in error_message and "deprecated" in error_message.lower():
            return {
                "successful": False,
                "error": f"API endpoint deprecated: {error_message}",
                "action": "update_board_sidebar_activity_preference",
                "board_id": id_board,
                "message": f"Failed to update sidebar activity preference - API endpoint is deprecated",
                "guidance": "The showSidebarActivity API endpoint has been deprecated by Trello and is no longer available.",
                "suggestion": "This feature may no longer be supported by Trello. Check Trello's documentation for alternative ways to manage sidebar activity preferences, or contact Trello support for assistance."
            }
        elif "409" in error_message and "closed" in error_message.lower():
            return {
                "successful": False,
                "error": f"Board is closed: {error_message}",
                "action": "update_board_sidebar_activity_preference",
                "board_id": id_board,
                "message": f"Failed to update sidebar activity preference - board is archived",
                "guidance": "Closed boards cannot be edited. You must unarchive the board first.",
                "suggestion": "Use TRELLO_UPDATE_BOARDS_CLOSED_BY_ID_BOARD to unarchive the board first."
            }
        else:
            return {
                "successful": False,
                "error": f"Failed to update sidebar activity preference: {error_message}",
                "action": "update_board_sidebar_activity_preference",
                "board_id": id_board,
                "message": f"Failed to update sidebar activity preference for board {id_board}"
            }


@mcp.tool(
    "TRELLO_UPDATE_BOARDS_MY_PREFS_SHOW_SIDEBAR_BY_ID_BOARD",
    description="Update board sidebar visibility. Updates the authenticated user's personal preference for showing or hiding the sidebar on a specific trello board.",
)
def TRELLO_UPDATE_BOARDS_MY_PREFS_SHOW_SIDEBAR_BY_ID_BOARD(
    id_board: Annotated[str, "The ID of the board to update sidebar visibility preference for."],
    value: Annotated[str, "The sidebar visibility preference value (e.g., 'true' to show, 'false' to hide)."]
):
    """Update board sidebar visibility. Updates the authenticated user's personal preference for showing or hiding the sidebar on a specific trello board."""
    err = _validate_required({"id_board": id_board, "value": value}, ["id_board", "value"])
    if err:
        return err
    
    try:
        endpoint = f"/boards/{id_board}/myPrefs/showSidebar"
        
        # Build data payload
        data = {
            "value": value
        }
        
        result = trello_request("PUT", endpoint, data=data)
        
        # Determine the preference set
        preference_set = "show" if value.lower() == "true" else "hide"
        
        return {
            "successful": True,
            "data": result,
            "action": "update_board_sidebar_visibility_preference",
            "board_id": id_board,
            "sidebar_visibility_preference": value,
            "preference_set": preference_set,
            "message": f"Successfully updated sidebar visibility preference to {preference_set} for board {id_board}"
        }
    except Exception as e:
        error_message = str(e)
        
        # Provide specific guidance for common errors
        if "403" in error_message:
            return {
                "successful": False,
                "error": f"Permission denied: {error_message}",
                "action": "update_board_sidebar_visibility_preference",
                "board_id": id_board,
                "message": f"Failed to update sidebar visibility preference - insufficient permissions",
                "guidance": "You must be a member of the board to update your personal preferences.",
                "suggestion": "Verify you have access to the board or ask a board admin to add you as a member."
            }
        elif "404" in error_message:
            return {
                "successful": False,
                "error": f"Board not found: {error_message}",
                "action": "update_board_sidebar_visibility_preference",
                "board_id": id_board,
                "message": f"Failed to update sidebar visibility preference - board not found",
                "guidance": "The board ID may be invalid or the board may have been deleted.",
                "suggestion": "Verify the board ID is correct and the board still exists."
            }
        elif "400" in error_message and "value" in error_message.lower():
            return {
                "successful": False,
                "error": f"Invalid preference value: {error_message}",
                "action": "update_board_sidebar_visibility_preference",
                "board_id": id_board,
                "message": f"Failed to update sidebar visibility preference - invalid value '{value}'",
                "guidance": "Valid preference values are 'true' to show the sidebar or 'false' to hide it.",
                "suggestion": "Use 'true' to show the sidebar or 'false' to hide it."
            }
        elif "410" in error_message and "deprecated" in error_message.lower():
            return {
                "successful": False,
                "error": f"API endpoint deprecated: {error_message}",
                "action": "update_board_sidebar_visibility_preference",
                "board_id": id_board,
                "message": f"Failed to update sidebar visibility preference - API endpoint is deprecated",
                "guidance": "The sidebar API endpoint has been deprecated by Trello and is no longer available.",
                "suggestion": "This feature may no longer be supported by Trello. Check Trello's documentation for alternative ways to manage sidebar preferences, or contact Trello support for assistance."
            }
        elif "409" in error_message and "closed" in error_message.lower():
            return {
                "successful": False,
                "error": f"Board is closed: {error_message}",
                "action": "update_board_sidebar_visibility_preference",
                "board_id": id_board,
                "message": f"Failed to update sidebar visibility preference - board is archived",
                "guidance": "Closed boards cannot be edited. You must unarchive the board first.",
                "suggestion": "Use TRELLO_UPDATE_BOARDS_CLOSED_BY_ID_BOARD to unarchive the board first."
            }
        else:
            return {
                "successful": False,
                "error": f"Failed to update sidebar visibility preference: {error_message}",
                "action": "update_board_sidebar_visibility_preference",
                "board_id": id_board,
                "message": f"Failed to update sidebar visibility preference for board {id_board}"
            }


@mcp.tool(
    "TRELLO_UPDATE_BOARDS_MY_PREFS_SHOW_SIDEBAR_MEMBERS_BY_ID_BOARD",
    description="Update board sidebar members preference. Updates the authenticated user's preference for showing or hiding members in a specific trello board's sidebar, affecting only the current user's view.",
)
def TRELLO_UPDATE_BOARDS_MY_PREFS_SHOW_SIDEBAR_MEMBERS_BY_ID_BOARD(
    id_board: Annotated[str, "The ID of the board to update sidebar members preference for."],
    value: Annotated[str, "The sidebar members preference value (e.g., 'true' to show, 'false' to hide)."]
):
    """Update board sidebar members preference. Updates the authenticated user's preference for showing or hiding members in a specific trello board's sidebar, affecting only the current user's view."""
    err = _validate_required({"id_board": id_board, "value": value}, ["id_board", "value"])
    if err:
        return err
    
    try:
        endpoint = f"/boards/{id_board}/myPrefs/showSidebarMembers"
        
        # Build data payload
        data = {
            "value": value
        }
        
        result = trello_request("PUT", endpoint, data=data)
        
        # Determine the preference set
        preference_set = "show" if value.lower() == "true" else "hide"
        
        return {
            "successful": True,
            "data": result,
            "action": "update_board_sidebar_members_preference",
            "board_id": id_board,
            "sidebar_members_preference": value,
            "preference_set": preference_set,
            "message": f"Successfully updated sidebar members preference to {preference_set} for board {id_board}"
        }
    except Exception as e:
        error_message = str(e)
        
        # Provide specific guidance for common errors
        if "403" in error_message:
            return {
                "successful": False,
                "error": f"Permission denied: {error_message}",
                "action": "update_board_sidebar_members_preference",
                "board_id": id_board,
                "message": f"Failed to update sidebar members preference - insufficient permissions",
                "guidance": "You must be a member of the board to update your personal preferences.",
                "suggestion": "Verify you have access to the board or ask a board admin to add you as a member."
            }
        elif "404" in error_message:
            return {
                "successful": False,
                "error": f"Board not found: {error_message}",
                "action": "update_board_sidebar_members_preference",
                "board_id": id_board,
                "message": f"Failed to update sidebar members preference - board not found",
                "guidance": "The board ID may be invalid or the board may have been deleted.",
                "suggestion": "Verify the board ID is correct and the board still exists."
            }
        elif "400" in error_message and "value" in error_message.lower():
            return {
                "successful": False,
                "error": f"Invalid preference value: {error_message}",
                "action": "update_board_sidebar_members_preference",
                "board_id": id_board,
                "message": f"Failed to update sidebar members preference - invalid value '{value}'",
                "guidance": "Valid preference values are 'true' to show members in the sidebar or 'false' to hide them.",
                "suggestion": "Use 'true' to show members in the sidebar or 'false' to hide them."
            }
        elif "410" in error_message and "deprecated" in error_message.lower():
            return {
                "successful": False,
                "error": f"API endpoint deprecated: {error_message}",
                "action": "update_board_sidebar_members_preference",
                "board_id": id_board,
                "message": f"Failed to update sidebar members preference - API endpoint is deprecated",
                "guidance": "The showSidebarMembers API endpoint has been deprecated by Trello and is no longer available.",
                "suggestion": "This feature may no longer be supported by Trello. Check Trello's documentation for alternative ways to manage sidebar members preferences, or contact Trello support for assistance."
            }
        elif "409" in error_message and "closed" in error_message.lower():
            return {
                "successful": False,
                "error": f"Board is closed: {error_message}",
                "action": "update_board_sidebar_members_preference",
                "board_id": id_board,
                "message": f"Failed to update sidebar members preference - board is archived",
                "guidance": "Closed boards cannot be edited. You must unarchive the board first.",
                "suggestion": "Use TRELLO_UPDATE_BOARDS_CLOSED_BY_ID_BOARD to unarchive the board first."
            }
        else:
            return {
                "successful": False,
                "error": f"Failed to update sidebar members preference: {error_message}",
                "action": "update_board_sidebar_members_preference",
                "board_id": id_board,
                "message": f"Failed to update sidebar members preference for board {id_board}"
            }


@mcp.tool(
    "TRELLO_UPDATE_BOARDS_NAME_BY_ID_BOARD",
    description="Update board name. Updates the name of an existing trello board, identified by `idboard`; this change only affects the board's name, not its other attributes.",
)
def TRELLO_UPDATE_BOARDS_NAME_BY_ID_BOARD(
    id_board: Annotated[str, "The ID of the board to update the name for."],
    value: Annotated[str, "The new name for the board."]
):
    """Update board name. Updates the name of an existing trello board, identified by `idboard`; this change only affects the board's name, not its other attributes."""
    err = _validate_required({"id_board": id_board, "value": value}, ["id_board", "value"])
    if err:
        return err
    
    try:
        endpoint = f"/boards/{id_board}"
        
        # Build data payload
        data = {
            "name": value
        }
        
        result = trello_request("PUT", endpoint, data=data)
        
        return {
            "successful": True,
            "data": result,
            "action": "update_board_name",
            "board_id": id_board,
            "new_board_name": value,
            "message": f"Successfully updated board name to '{value}' for board {id_board}"
        }
    except Exception as e:
        error_message = str(e)
        
        # Provide specific guidance for common errors
        if "403" in error_message:
            return {
                "successful": False,
                "error": f"Permission denied: {error_message}",
                "action": "update_board_name",
                "board_id": id_board,
                "message": f"Failed to update board name - insufficient permissions",
                "guidance": "You must be an admin of the board to update its name.",
                "suggestion": "Verify you have admin access to the board or ask a board admin to make the change."
            }
        elif "404" in error_message:
            return {
                "successful": False,
                "error": f"Board not found: {error_message}",
                "action": "update_board_name",
                "board_id": id_board,
                "message": f"Failed to update board name - board not found",
                "guidance": "The board ID may be invalid or the board may have been deleted.",
                "suggestion": "Verify the board ID is correct and the board still exists."
            }
        elif "400" in error_message and "name" in error_message.lower():
            return {
                "successful": False,
                "error": f"Invalid board name: {error_message}",
                "action": "update_board_name",
                "board_id": id_board,
                "message": f"Failed to update board name - invalid name '{value}'",
                "guidance": "Check that the board name is valid and doesn't contain problematic characters.",
                "suggestion": "Ensure the board name is valid and follows Trello's naming conventions."
            }
        elif "409" in error_message and "closed" in error_message.lower():
            return {
                "successful": False,
                "error": f"Board is closed: {error_message}",
                "action": "update_board_name",
                "board_id": id_board,
                "message": f"Failed to update board name - board is archived",
                "guidance": "Closed boards cannot be edited. You must unarchive the board first.",
                "suggestion": "Use TRELLO_UPDATE_BOARDS_CLOSED_BY_ID_BOARD to unarchive the board first."
            }
        elif "409" in error_message and "duplicate" in error_message.lower():
            return {
                "successful": False,
                "error": f"Duplicate board name: {error_message}",
                "action": "update_board_name",
                "board_id": id_board,
                "message": f"Failed to update board name - name '{value}' already exists",
                "guidance": "A board with this name already exists in your workspace or organization.",
                "suggestion": "Choose a different name for the board or check if there's already a board with this name."
            }
        else:
            return {
                "successful": False,
                "error": f"Failed to update board name: {error_message}",
                "action": "update_board_name",
                "board_id": id_board,
                "message": f"Failed to update board name for board {id_board}"
            }


@mcp.tool(
    "TRELLO_UPDATE_BOARDS_PREFS_BACKGROUND_BY_ID_BOARD",
    description="Update board background. Updates the cosmetic background preference for a specific trello board; this change does not affect board functionality or content.",
)
def TRELLO_UPDATE_BOARDS_PREFS_BACKGROUND_BY_ID_BOARD(
    id_board: Annotated[str, "The ID of the board to update background preference for."],
    value: Annotated[str, "The background preference value (e.g., 'blue', 'orange', 'green', 'red', 'purple', 'pink', 'lime', 'sky', 'grey', or a custom background ID)."]
):
    """Update board background. Updates the cosmetic background preference for a specific trello board; this change does not affect board functionality or content."""
    err = _validate_required({"id_board": id_board, "value": value}, ["id_board", "value"])
    if err:
        return err
    
    try:
        endpoint = f"/boards/{id_board}"
        
        # Build data payload for background preference
        data = {
            "prefs": {
                "background": value
            }
        }
        
        result = trello_request("PUT", endpoint, data=data)
        
        return {
            "successful": True,
            "data": result,
            "action": "update_board_background",
            "board_id": id_board,
            "new_background": value,
            "message": f"Successfully updated board background to '{value}' for board {id_board}"
        }
    except Exception as e:
        error_message = str(e)
        
        # Provide specific guidance for common errors
        if "403" in error_message:
            return {
                "successful": False,
                "error": f"Permission denied: {error_message}",
                "action": "update_board_background",
                "board_id": id_board,
                "message": f"Failed to update board background - insufficient permissions",
                "guidance": "You must be an admin of the board to update its background.",
                "suggestion": "Verify you have admin access to the board or ask a board admin to make the change."
            }
        elif "404" in error_message:
            return {
                "successful": False,
                "error": f"Board not found: {error_message}",
                "action": "update_board_background",
                "board_id": id_board,
                "message": f"Failed to update board background - board not found",
                "guidance": "The board ID may be invalid or the board may have been deleted.",
                "suggestion": "Verify the board ID is correct and the board still exists."
            }
        elif "400" in error_message and "background" in error_message.lower():
            return {
                "successful": False,
                "error": f"Invalid background: {error_message}",
                "action": "update_board_background",
                "board_id": id_board,
                "message": f"Failed to update board background - invalid background '{value}'",
                "guidance": "Check that the background value is valid. Common values include: blue, orange, green, red, purple, pink, lime, sky, grey, or a custom background ID.",
                "suggestion": "Use a valid background color name or custom background ID. Check Trello's documentation for available background options."
            }
        elif "409" in error_message and "closed" in error_message.lower():
            return {
                "successful": False,
                "error": f"Board is closed: {error_message}",
                "action": "update_board_background",
                "board_id": id_board,
                "message": f"Failed to update board background - board is archived",
                "guidance": "Closed boards cannot be edited. You must unarchive the board first.",
                "suggestion": "Use TRELLO_UPDATE_BOARDS_CLOSED_BY_ID_BOARD to unarchive the board first."
            }
        else:
            return {
                "successful": False,
                "error": f"Failed to update board background: {error_message}",
                "action": "update_board_background",
                "board_id": id_board,
                "message": f"Failed to update board background for board {id_board}"
            }


@mcp.tool(
    "TRELLO_UPDATE_BOARDS_PREFS_CALENDAR_FEED_ENABLED_BY_ID_BOARD",
    description="Update board calendar feed enabled status. Updates the 'calendarfeedenabled' preference for a trello board, which, when enabled, makes board cards with due dates accessible via an icalendar feed for external calendar integration.",
)
def TRELLO_UPDATE_BOARDS_PREFS_CALENDAR_FEED_ENABLED_BY_ID_BOARD(
    id_board: Annotated[str, "The ID of the board to update calendar feed enabled status for."],
    value: Annotated[str, "The calendar feed enabled status (e.g., 'true' to enable, 'false' to disable)."]
):
    """Update board calendar feed enabled status. Updates the 'calendarfeedenabled' preference for a trello board, which, when enabled, makes board cards with due dates accessible via an icalendar feed for external calendar integration."""
    err = _validate_required({"id_board": id_board, "value": value}, ["id_board", "value"])
    if err:
        return err
    
    try:
        endpoint = f"/boards/{id_board}"
        
        # Build data payload for calendar feed enabled preference
        data = {
            "prefs": {
                "calendarFeedEnabled": value
            }
        }
        
        result = trello_request("PUT", endpoint, data=data)
        
        # Determine the status set
        status_set = "enabled" if value.lower() == "true" else "disabled"
        
        return {
            "successful": True,
            "data": result,
            "action": "update_board_calendar_feed_enabled",
            "board_id": id_board,
            "calendar_feed_enabled": value,
            "status_set": status_set,
            "message": f"Successfully {status_set} calendar feed for board {id_board}"
        }
    except Exception as e:
        error_message = str(e)
        
        # Provide specific guidance for common errors
        if "403" in error_message:
            return {
                "successful": False,
                "error": f"Permission denied: {error_message}",
                "action": "update_board_calendar_feed_enabled",
                "board_id": id_board,
                "message": f"Failed to update calendar feed status - insufficient permissions",
                "guidance": "You must be an admin of the board to update its calendar feed settings.",
                "suggestion": "Verify you have admin access to the board or ask a board admin to make the change."
            }
        elif "404" in error_message:
            return {
                "successful": False,
                "error": f"Board not found: {error_message}",
                "action": "update_board_calendar_feed_enabled",
                "board_id": id_board,
                "message": f"Failed to update calendar feed status - board not found",
                "guidance": "The board ID may be invalid or the board may have been deleted.",
                "suggestion": "Verify the board ID is correct and the board still exists."
            }
        elif "400" in error_message and "value" in error_message.lower():
            return {
                "successful": False,
                "error": f"Invalid calendar feed value: {error_message}",
                "action": "update_board_calendar_feed_enabled",
                "board_id": id_board,
                "message": f"Failed to update calendar feed status - invalid value '{value}'",
                "guidance": "Valid values are 'true' to enable calendar feed or 'false' to disable it.",
                "suggestion": "Use 'true' to enable calendar feed or 'false' to disable it."
            }
        elif "409" in error_message and "closed" in error_message.lower():
            return {
                "successful": False,
                "error": f"Board is closed: {error_message}",
                "action": "update_board_calendar_feed_enabled",
                "board_id": id_board,
                "message": f"Failed to update calendar feed status - board is archived",
                "guidance": "Closed boards cannot be edited. You must unarchive the board first.",
                "suggestion": "Use TRELLO_UPDATE_BOARDS_CLOSED_BY_ID_BOARD to unarchive the board first."
            }
        else:
            return {
                "successful": False,
                "error": f"Failed to update calendar feed status: {error_message}",
                "action": "update_board_calendar_feed_enabled",
                "board_id": id_board,
                "message": f"Failed to update calendar feed status for board {id_board}"
            }


@mcp.tool(
    "TRELLO_UPDATE_BOARDS_PREFS_CARD_AGING_BY_ID_BOARD",
    description="Update board card aging preference. Updates the card aging visual preference to 'pirate' or 'regular' mode for a specified trello board.",
)
def TRELLO_UPDATE_BOARDS_PREFS_CARD_AGING_BY_ID_BOARD(
    id_board: Annotated[str, "The ID of the board to update card aging preference for."],
    value: Annotated[str, "The card aging preference value ('pirate' or 'regular')."]
):
    """Update board card aging preference. Updates the card aging visual preference to 'pirate' or 'regular' mode for a specified trello board."""
    err = _validate_required({"id_board": id_board, "value": value}, ["id_board", "value"])
    if err:
        return err
    
    # Validate the value is either 'pirate' or 'regular'
    if value.lower() not in ['pirate', 'regular']:
        return {
            "successful": False,
            "error": "Invalid card aging value",
            "action": "update_board_card_aging",
            "board_id": id_board,
            "message": f"Invalid card aging value '{value}' - must be 'pirate' or 'regular'",
            "guidance": "Valid card aging values are 'pirate' or 'regular'.",
            "suggestion": "Use 'pirate' for pirate-themed card aging or 'regular' for standard card aging."
        }
    
    try:
        endpoint = f"/boards/{id_board}"
        
        # Build data payload for card aging preference
        data = {
            "prefs": {
                "cardAging": value
            }
        }
        
        result = trello_request("PUT", endpoint, data=data)
        
        return {
            "successful": True,
            "data": result,
            "action": "update_board_card_aging",
            "board_id": id_board,
            "card_aging_preference": value,
            "message": f"Successfully updated card aging preference to '{value}' for board {id_board}"
        }
    except Exception as e:
        error_message = str(e)
        
        # Provide specific guidance for common errors
        if "403" in error_message:
            return {
                "successful": False,
                "error": f"Permission denied: {error_message}",
                "action": "update_board_card_aging",
                "board_id": id_board,
                "message": f"Failed to update card aging preference - insufficient permissions",
                "guidance": "You must be an admin of the board to update its card aging settings.",
                "suggestion": "Verify you have admin access to the board or ask a board admin to make the change."
            }
        elif "404" in error_message:
            return {
                "successful": False,
                "error": f"Board not found: {error_message}",
                "action": "update_board_card_aging",
                "board_id": id_board,
                "message": f"Failed to update card aging preference - board not found",
                "guidance": "The board ID may be invalid or the board may have been deleted.",
                "suggestion": "Verify the board ID is correct and the board still exists."
            }
        elif "400" in error_message and "cardaging" in error_message.lower():
            return {
                "successful": False,
                "error": f"Invalid card aging value: {error_message}",
                "action": "update_board_card_aging",
                "board_id": id_board,
                "message": f"Failed to update card aging preference - invalid value '{value}'",
                "guidance": "Valid card aging values are 'pirate' or 'regular'.",
                "suggestion": "Use 'pirate' for pirate-themed card aging or 'regular' for standard card aging."
            }
        elif "409" in error_message and "closed" in error_message.lower():
            return {
                "successful": False,
                "error": f"Board is closed: {error_message}",
                "action": "update_board_card_aging",
                "board_id": id_board,
                "message": f"Failed to update card aging preference - board is archived",
                "guidance": "Closed boards cannot be edited. You must unarchive the board first.",
                "suggestion": "Use TRELLO_UPDATE_BOARDS_CLOSED_BY_ID_BOARD to unarchive the board first."
            }
        else:
            return {
                "successful": False,
                "error": f"Failed to update card aging preference: {error_message}",
                "action": "update_board_card_aging",
                "board_id": id_board,
                "message": f"Failed to update card aging preference for board {id_board}"
            }


@mcp.tool(
    "TRELLO_UPDATE_BOARDS_PREFS_CARD_COVERS_BY_ID_BOARD",
    description="Update board card cover preference. Updates the preference on a specific trello board for whether existing card covers are displayed; this controls visibility only and does not add or remove the actual covers from cards.",
)
def TRELLO_UPDATE_BOARDS_PREFS_CARD_COVERS_BY_ID_BOARD(
    id_board: Annotated[str, "The ID of the board to update card cover preference for."],
    value: Annotated[str, "The card cover preference value (e.g., 'true' to show covers, 'false' to hide covers)."]
):
    """Update board card cover preference. Updates the preference on a specific trello board for whether existing card covers are displayed; this controls visibility only and does not add or remove the actual covers from cards."""
    err = _validate_required({"id_board": id_board, "value": value}, ["id_board", "value"])
    if err:
        return err
    
    try:
        endpoint = f"/boards/{id_board}"
        
        # Build data payload for card covers preference
        data = {
            "prefs": {
                "cardCovers": value
            }
        }
        
        result = trello_request("PUT", endpoint, data=data)
        
        # Determine the preference set
        preference_set = "show" if value.lower() == "true" else "hide"
        
        return {
            "successful": True,
            "data": result,
            "action": "update_board_card_covers",
            "board_id": id_board,
            "card_covers_preference": value,
            "preference_set": preference_set,
            "message": f"Successfully updated card covers preference to {preference_set} for board {id_board}"
        }
    except Exception as e:
        error_message = str(e)
        
        # Provide specific guidance for common errors
        if "403" in error_message:
            return {
                "successful": False,
                "error": f"Permission denied: {error_message}",
                "action": "update_board_card_covers",
                "board_id": id_board,
                "message": f"Failed to update card covers preference - insufficient permissions",
                "guidance": "You must be an admin of the board to update its card cover settings.",
                "suggestion": "Verify you have admin access to the board or ask a board admin to make the change."
            }
        elif "404" in error_message:
            return {
                "successful": False,
                "error": f"Board not found: {error_message}",
                "action": "update_board_card_covers",
                "board_id": id_board,
                "message": f"Failed to update card covers preference - board not found",
                "guidance": "The board ID may be invalid or the board may have been deleted.",
                "suggestion": "Verify the board ID is correct and the board still exists."
            }
        elif "400" in error_message and "value" in error_message.lower():
            return {
                "successful": False,
                "error": f"Invalid card covers value: {error_message}",
                "action": "update_board_card_covers",
                "board_id": id_board,
                "message": f"Failed to update card covers preference - invalid value '{value}'",
                "guidance": "Valid values are 'true' to show card covers or 'false' to hide them.",
                "suggestion": "Use 'true' to show card covers or 'false' to hide them."
            }
        elif "409" in error_message and "closed" in error_message.lower():
            return {
                "successful": False,
                "error": f"Board is closed: {error_message}",
                "action": "update_board_card_covers",
                "board_id": id_board,
                "message": f"Failed to update card covers preference - board is archived",
                "guidance": "Closed boards cannot be edited. You must unarchive the board first.",
                "suggestion": "Use TRELLO_UPDATE_BOARDS_CLOSED_BY_ID_BOARD to unarchive the board first."
            }
        else:
            return {
                "successful": False,
                "error": f"Failed to update card covers preference: {error_message}",
                "action": "update_board_card_covers",
                "board_id": id_board,
                "message": f"Failed to update card covers preference for board {id_board}"
            }


@mcp.tool(
    "TRELLO_UPDATE_BOARDS_PREFS_COMMENTS_BY_ID_BOARD",
    description="Update board comment preferences. Changes the permission settings for who can add comments to cards on a specific trello board, without affecting other board settings.",
)
def TRELLO_UPDATE_BOARDS_PREFS_COMMENTS_BY_ID_BOARD(
    id_board: Annotated[str, "The ID of the board to update comment preferences for."],
    value: Annotated[str, "The comment permission value (e.g., 'members', 'observers', 'disabled')."]
):
    """Update board comment preferences. Changes the permission settings for who can add comments to cards on a specific trello board, without affecting other board settings."""
    err = _validate_required({"id_board": id_board, "value": value}, ["id_board", "value"])
    if err:
        return err
    
    # Validate the value is a valid comment permission
    valid_permissions = ['members', 'observers', 'disabled']
    if value.lower() not in valid_permissions:
        return {
            "successful": False,
            "error": "Invalid comment permission value",
            "action": "update_board_comments",
            "board_id": id_board,
            "message": f"Invalid comment permission value '{value}' - must be one of: {', '.join(valid_permissions)}",
            "guidance": f"Valid comment permission values are: {', '.join(valid_permissions)}.",
            "suggestion": f"Use one of: {', '.join(valid_permissions)} to set comment permissions."
        }
    
    try:
        endpoint = f"/boards/{id_board}"
        
        # Build data payload for comment preferences
        data = {
            "prefs": {
                "comments": value
            }
        }
        
        result = trello_request("PUT", endpoint, data=data)
        
        return {
            "successful": True,
            "data": result,
            "action": "update_board_comments",
            "board_id": id_board,
            "comment_permission": value,
            "message": f"Successfully updated comment permissions to '{value}' for board {id_board}"
        }
    except Exception as e:
        error_message = str(e)
        
        # Provide specific guidance for common errors
        if "403" in error_message:
            return {
                "successful": False,
                "error": f"Permission denied: {error_message}",
                "action": "update_board_comments",
                "board_id": id_board,
                "message": f"Failed to update comment preferences - insufficient permissions",
                "guidance": "You must be an admin of the board to update its comment settings.",
                "suggestion": "Verify you have admin access to the board or ask a board admin to make the change."
            }
        elif "404" in error_message:
            return {
                "successful": False,
                "error": f"Board not found: {error_message}",
                "action": "update_board_comments",
                "board_id": id_board,
                "message": f"Failed to update comment preferences - board not found",
                "guidance": "The board ID may be invalid or the board may have been deleted.",
                "suggestion": "Verify the board ID is correct and the board still exists."
            }
        elif "400" in error_message and "comments" in error_message.lower():
            return {
                "successful": False,
                "error": f"Invalid comment permission: {error_message}",
                "action": "update_board_comments",
                "board_id": id_board,
                "message": f"Failed to update comment preferences - invalid permission '{value}'",
                "guidance": f"Valid comment permission values are: {', '.join(valid_permissions)}.",
                "suggestion": f"Use one of: {', '.join(valid_permissions)} to set comment permissions."
            }
        elif "409" in error_message and "closed" in error_message.lower():
            return {
                "successful": False,
                "error": f"Board is closed: {error_message}",
                "action": "update_board_comments",
                "board_id": id_board,
                "message": f"Failed to update comment preferences - board is archived",
                "guidance": "Closed boards cannot be edited. You must unarchive the board first.",
                "suggestion": "Use TRELLO_UPDATE_BOARDS_CLOSED_BY_ID_BOARD to unarchive the board first."
            }
        else:
            return {
                "successful": False,
                "error": f"Failed to update comment preferences: {error_message}",
                "action": "update_board_comments",
                "board_id": id_board,
                "message": f"Failed to update comment preferences for board {id_board}"
            }


@mcp.tool(
    "TRELLO_UPDATE_BOARDS_PREFS_INVITATIONS_BY_ID_BOARD",
    description="Update board invitation preferences. Updates who can invite new members ('admins' or 'members') to a specific trello board.",
)
def TRELLO_UPDATE_BOARDS_PREFS_INVITATIONS_BY_ID_BOARD(
    id_board: Annotated[str, "The ID of the board to update invitation preferences for."],
    value: Annotated[str, "The invitation permission value ('admins' or 'members')."]
):
    """Update board invitation preferences. Updates who can invite new members ('admins' or 'members') to a specific trello board."""
    err = _validate_required({"id_board": id_board, "value": value}, ["id_board", "value"])
    if err:
        return err
    
    # Validate the value is a valid invitation permission
    valid_permissions = ['admins', 'members']
    if value.lower() not in valid_permissions:
        return {
            "successful": False,
            "error": "Invalid invitation permission value",
            "action": "update_board_invitations",
            "board_id": id_board,
            "message": f"Invalid invitation permission value '{value}' - must be one of: {', '.join(valid_permissions)}",
            "guidance": f"Valid invitation permission values are: {', '.join(valid_permissions)}.",
            "suggestion": f"Use one of: {', '.join(valid_permissions)} to set invitation permissions."
        }
    
    try:
        endpoint = f"/boards/{id_board}"
        
        # Build data payload for invitation preferences
        data = {
            "prefs": {
                "invitations": value
            }
        }
        
        result = trello_request("PUT", endpoint, data=data)
        
        return {
            "successful": True,
            "data": result,
            "action": "update_board_invitations",
            "board_id": id_board,
            "invitation_permission": value,
            "message": f"Successfully updated invitation permissions to '{value}' for board {id_board}"
        }
    except Exception as e:
        error_message = str(e)
        
        # Provide specific guidance for common errors
        if "403" in error_message:
            return {
                "successful": False,
                "error": f"Permission denied: {error_message}",
                "action": "update_board_invitations",
                "board_id": id_board,
                "message": f"Failed to update invitation preferences - insufficient permissions",
                "guidance": "You must be an admin of the board to update its invitation settings.",
                "suggestion": "Verify you have admin access to the board or ask a board admin to make the change."
            }
        elif "404" in error_message:
            return {
                "successful": False,
                "error": f"Board not found: {error_message}",
                "action": "update_board_invitations",
                "board_id": id_board,
                "message": f"Failed to update invitation preferences - board not found",
                "guidance": "The board ID may be invalid or the board may have been deleted.",
                "suggestion": "Verify the board ID is correct and the board still exists."
            }
        elif "400" in error_message and "invitations" in error_message.lower():
            return {
                "successful": False,
                "error": f"Invalid invitation permission: {error_message}",
                "action": "update_board_invitations",
                "board_id": id_board,
                "message": f"Failed to update invitation preferences - invalid permission '{value}'",
                "guidance": f"Valid invitation permission values are: {', '.join(valid_permissions)}.",
                "suggestion": f"Use one of: {', '.join(valid_permissions)} to set invitation permissions."
            }
        elif "409" in error_message and "closed" in error_message.lower():
            return {
                "successful": False,
                "error": f"Board is closed: {error_message}",
                "action": "update_board_invitations",
                "board_id": id_board,
                "message": f"Failed to update invitation preferences - board is archived",
                "guidance": "Closed boards cannot be edited. You must unarchive the board first.",
                "suggestion": "Use TRELLO_UPDATE_BOARDS_CLOSED_BY_ID_BOARD to unarchive the board first."
            }
        else:
            return {
                "successful": False,
                "error": f"Failed to update invitation preferences: {error_message}",
                "action": "update_board_invitations",
                "board_id": id_board,
                "message": f"Failed to update invitation preferences for board {id_board}"
            }


@mcp.tool(
    "TRELLO_UPDATE_BOARDS_PREFS_PERMISSION_LEVEL_BY_ID_BOARD",
    description="Update board prefs permission level. Updates the permission level preference (e.g., 'private' or 'public') for a trello board, identified by `idboard`, if the board exists and the authenticated user possesses administrative permissions for it.",
)
def TRELLO_UPDATE_BOARDS_PREFS_PERMISSION_LEVEL_BY_ID_BOARD(
    id_board: Annotated[str, "The ID of the board to update permission level preference for."],
    value: Annotated[str, "The permission level value (e.g., 'private', 'org', 'public')."]
):
    """Update board prefs permission level. Updates the permission level preference (e.g., 'private' or 'public') for a trello board, identified by `idboard`, if the board exists and the authenticated user possesses administrative permissions for it."""
    err = _validate_required({"id_board": id_board, "value": value}, ["id_board", "value"])
    if err:
        return err
    
    # Validate the value is a valid permission level
    valid_permissions = ['private', 'org', 'public']
    if value.lower() not in valid_permissions:
        return {
            "successful": False,
            "error": "Invalid permission level value",
            "action": "update_board_permission_level",
            "board_id": id_board,
            "message": f"Invalid permission level value '{value}' - must be one of: {', '.join(valid_permissions)}",
            "guidance": f"Valid permission level values are: {', '.join(valid_permissions)}.",
            "suggestion": f"Use one of: {', '.join(valid_permissions)} to set board permission level."
        }
    
    try:
        endpoint = f"/boards/{id_board}"
        
        # Build data payload for permission level preference
        data = {
            "prefs": {
                "permissionLevel": value
            }
        }
        
        result = trello_request("PUT", endpoint, data=data)
        
        return {
            "successful": True,
            "data": result,
            "action": "update_board_permission_level",
            "board_id": id_board,
            "permission_level": value,
            "message": f"Successfully updated permission level to '{value}' for board {id_board}"
        }
    except Exception as e:
        error_message = str(e)
        
        # Provide specific guidance for common errors
        if "403" in error_message:
            return {
                "successful": False,
                "error": f"Permission denied: {error_message}",
                "action": "update_board_permission_level",
                "board_id": id_board,
                "message": f"Failed to update permission level - insufficient permissions",
                "guidance": "You must be an admin of the board to update its permission level settings.",
                "suggestion": "Verify you have admin access to the board or ask a board admin to make the change."
            }
        elif "404" in error_message:
            return {
                "successful": False,
                "error": f"Board not found: {error_message}",
                "action": "update_board_permission_level",
                "board_id": id_board,
                "message": f"Failed to update permission level - board not found",
                "guidance": "The board ID may be invalid or the board may have been deleted.",
                "suggestion": "Verify the board ID is correct and the board still exists."
            }
        elif "400" in error_message and "permission" in error_message.lower():
            return {
                "successful": False,
                "error": f"Invalid permission level: {error_message}",
                "action": "update_board_permission_level",
                "board_id": id_board,
                "message": f"Failed to update permission level - invalid level '{value}'",
                "guidance": f"Valid permission level values are: {', '.join(valid_permissions)}.",
                "suggestion": f"Use one of: {', '.join(valid_permissions)} to set board permission level."
            }
        elif "409" in error_message and "closed" in error_message.lower():
            return {
                "successful": False,
                "error": f"Board is closed: {error_message}",
                "action": "update_board_permission_level",
                "board_id": id_board,
                "message": f"Failed to update permission level - board is archived",
                "guidance": "Closed boards cannot be edited. You must unarchive the board first.",
                "suggestion": "Use TRELLO_UPDATE_BOARDS_CLOSED_BY_ID_BOARD to unarchive the board first."
            }
        else:
            return {
                "successful": False,
                "error": f"Failed to update permission level: {error_message}",
                "action": "update_board_permission_level",
                "board_id": id_board,
                "message": f"Failed to update permission level for board {id_board}"
            }


@mcp.tool(
    "TRELLO_UPDATE_BOARDS_PREFS_SELF_JOIN_BY_ID_BOARD",
    description="Update board self-join preference. Updates a board's 'selfjoin' preference, determining if members can join freely or must be invited.",
)
def TRELLO_UPDATE_BOARDS_PREFS_SELF_JOIN_BY_ID_BOARD(
    id_board: Annotated[str, "The ID of the board to update self-join preference for."],
    value: Annotated[str, "The self-join preference value (e.g., 'true' to allow self-join, 'false' to require invitation)."]
):
    """Update board self-join preference. Updates a board's 'selfjoin' preference, determining if members can join freely or must be invited."""
    err = _validate_required({"id_board": id_board, "value": value}, ["id_board", "value"])
    if err:
        return err
    
    try:
        endpoint = f"/boards/{id_board}"
        
        # Build data payload for self-join preference
        data = {
            "prefs": {
                "selfJoin": value
            }
        }
        
        result = trello_request("PUT", endpoint, data=data)
        
        # Determine the preference set
        preference_set = "allow self-join" if value.lower() == "true" else "require invitation"
        
        return {
            "successful": True,
            "data": result,
            "action": "update_board_self_join",
            "board_id": id_board,
            "self_join_preference": value,
            "preference_set": preference_set,
            "message": f"Successfully updated self-join preference to {preference_set} for board {id_board}"
        }
    except Exception as e:
        error_message = str(e)
        
        # Provide specific guidance for common errors
        if "403" in error_message:
            return {
                "successful": False,
                "error": f"Permission denied: {error_message}",
                "action": "update_board_self_join",
                "board_id": id_board,
                "message": f"Failed to update self-join preference - insufficient permissions",
                "guidance": "You must be an admin of the board to update its self-join settings.",
                "suggestion": "Verify you have admin access to the board or ask a board admin to make the change."
            }
        elif "404" in error_message:
            return {
                "successful": False,
                "error": f"Board not found: {error_message}",
                "action": "update_board_self_join",
                "board_id": id_board,
                "message": f"Failed to update self-join preference - board not found",
                "guidance": "The board ID may be invalid or the board may have been deleted.",
                "suggestion": "Verify the board ID is correct and the board still exists."
            }
        elif "400" in error_message and "value" in error_message.lower():
            return {
                "successful": False,
                "error": f"Invalid self-join value: {error_message}",
                "action": "update_board_self_join",
                "board_id": id_board,
                "message": f"Failed to update self-join preference - invalid value '{value}'",
                "guidance": "Valid values are 'true' to allow self-join or 'false' to require invitation.",
                "suggestion": "Use 'true' to allow self-join or 'false' to require invitation."
            }
        elif "409" in error_message and "closed" in error_message.lower():
            return {
                "successful": False,
                "error": f"Board is closed: {error_message}",
                "action": "update_board_self_join",
                "board_id": id_board,
                "message": f"Failed to update self-join preference - board is archived",
                "guidance": "Closed boards cannot be edited. You must unarchive the board first.",
                "suggestion": "Use TRELLO_UPDATE_BOARDS_CLOSED_BY_ID_BOARD to unarchive the board first."
            }
        else:
            return {
                "successful": False,
                "error": f"Failed to update self-join preference: {error_message}",
                "action": "update_board_self_join",
                "board_id": id_board,
                "message": f"Failed to update self-join preference for board {id_board}"
            }


@mcp.tool(
    "TRELLO_UPDATE_BOARDS_PREFS_VOTING_BY_ID_BOARD",
    description="Update board voting preferences. Sets who can vote on cards for an existing trello board, changing only the voting preferences for all cards on the board.",
)
def TRELLO_UPDATE_BOARDS_PREFS_VOTING_BY_ID_BOARD(
    id_board: Annotated[str, "The ID of the board to update voting preferences for."],
    value: Annotated[str, "The voting permission value (e.g., 'members', 'observers', 'disabled')."]
):
    """Update board voting preferences. Sets who can vote on cards for an existing trello board, changing only the voting preferences for all cards on the board."""
    err = _validate_required({"id_board": id_board, "value": value}, ["id_board", "value"])
    if err:
        return err
    
    # Validate the value is a valid voting permission
    valid_permissions = ['members', 'observers', 'disabled']
    if value.lower() not in valid_permissions:
        return {
            "successful": False,
            "error": "Invalid voting permission value",
            "action": "update_board_voting",
            "board_id": id_board,
            "message": f"Invalid voting permission value '{value}' - must be one of: {', '.join(valid_permissions)}",
            "guidance": f"Valid voting permission values are: {', '.join(valid_permissions)}.",
            "suggestion": f"Use one of: {', '.join(valid_permissions)} to set voting permissions."
        }
    
    try:
        endpoint = f"/boards/{id_board}"
        
        # Build data payload for voting preferences
        data = {
            "prefs": {
                "voting": value
            }
        }
        
        result = trello_request("PUT", endpoint, data=data)
        
        return {
            "successful": True,
            "data": result,
            "action": "update_board_voting",
            "board_id": id_board,
            "voting_permission": value,
            "message": f"Successfully updated voting permissions to '{value}' for board {id_board}"
        }
    except Exception as e:
        error_message = str(e)
        
        # Provide specific guidance for common errors
        if "403" in error_message:
            return {
                "successful": False,
                "error": f"Permission denied: {error_message}",
                "action": "update_board_voting",
                "board_id": id_board,
                "message": f"Failed to update voting preferences - insufficient permissions",
                "guidance": "You must be an admin of the board to update its voting settings.",
                "suggestion": "Verify you have admin access to the board or ask a board admin to make the change."
            }
        elif "404" in error_message:
            return {
                "successful": False,
                "error": f"Board not found: {error_message}",
                "action": "update_board_voting",
                "board_id": id_board,
                "message": f"Failed to update voting preferences - board not found",
                "guidance": "The board ID may be invalid or the board may have been deleted.",
                "suggestion": "Verify the board ID is correct and the board still exists."
            }
        elif "400" in error_message and "voting" in error_message.lower():
            return {
                "successful": False,
                "error": f"Invalid voting permission: {error_message}",
                "action": "update_board_voting",
                "board_id": id_board,
                "message": f"Failed to update voting preferences - invalid permission '{value}'",
                "guidance": f"Valid voting permission values are: {', '.join(valid_permissions)}.",
                "suggestion": f"Use one of: {', '.join(valid_permissions)} to set voting permissions."
            }
        elif "409" in error_message and "closed" in error_message.lower():
            return {
                "successful": False,
                "error": f"Board is closed: {error_message}",
                "action": "update_board_voting",
                "board_id": id_board,
                "message": f"Failed to update voting preferences - board is archived",
                "guidance": "Closed boards cannot be edited. You must unarchive the board first.",
                "suggestion": "Use TRELLO_UPDATE_BOARDS_CLOSED_BY_ID_BOARD to unarchive the board first."
            }
        else:
            return {
                "successful": False,
                "error": f"Failed to update voting preferences: {error_message}",
                "action": "update_board_voting",
                "board_id": id_board,
                "message": f"Failed to update voting preferences for board {id_board}"
            }


@mcp.tool(
    "TRELLO_UPDATE_BOARDS_SUBSCRIBED_BY_ID_BOARD",
    description="Update board subscription status. Updates the authenticated user's subscription status (subscribe/unsubscribe for notifications) for a specified trello board, to which the user must have access.",
)
def TRELLO_UPDATE_BOARDS_SUBSCRIBED_BY_ID_BOARD(
    id_board: Annotated[str, "The ID of the board to update subscription status for."],
    value: Annotated[str, "The subscription status value (e.g., 'true' to subscribe, 'false' to unsubscribe)."]
):
    """Update board subscription status. Updates the authenticated user's subscription status (subscribe/unsubscribe for notifications) for a specified trello board, to which the user must have access."""
    err = _validate_required({"id_board": id_board, "value": value}, ["id_board", "value"])
    if err:
        return err
    
    try:
        endpoint = f"/boards/{id_board}"
        
        # Build data payload for subscription status
        data = {
            "subscribed": value
        }
        
        result = trello_request("PUT", endpoint, data=data)
        
        # Determine the subscription status set
        subscription_status = "subscribed" if value.lower() == "true" else "unsubscribed"
        
        return {
            "successful": True,
            "data": result,
            "action": "update_board_subscription",
            "board_id": id_board,
            "subscription_status": value,
            "status_set": subscription_status,
            "message": f"Successfully {subscription_status} to board {id_board}"
        }
    except Exception as e:
        error_message = str(e)
        
        # Provide specific guidance for common errors
        if "403" in error_message:
            return {
                "successful": False,
                "error": f"Permission denied: {error_message}",
                "action": "update_board_subscription",
                "board_id": id_board,
                "message": f"Failed to update subscription status - insufficient permissions",
                "guidance": "You must have access to the board to update your subscription status.",
                "suggestion": "Verify you have access to the board or ask a board admin to add you as a member."
            }
        elif "404" in error_message:
            return {
                "successful": False,
                "error": f"Board not found: {error_message}",
                "action": "update_board_subscription",
                "board_id": id_board,
                "message": f"Failed to update subscription status - board not found",
                "guidance": "The board ID may be invalid or the board may have been deleted.",
                "suggestion": "Verify the board ID is correct and the board still exists."
            }
        elif "400" in error_message and "value" in error_message.lower():
            return {
                "successful": False,
                "error": f"Invalid subscription value: {error_message}",
                "action": "update_board_subscription",
                "board_id": id_board,
                "message": f"Failed to update subscription status - invalid value '{value}'",
                "guidance": "Valid values are 'true' to subscribe or 'false' to unsubscribe.",
                "suggestion": "Use 'true' to subscribe to board notifications or 'false' to unsubscribe."
            }
        elif "409" in error_message and "closed" in error_message.lower():
            return {
                "successful": False,
                "error": f"Board is closed: {error_message}",
                "action": "update_board_subscription",
                "board_id": id_board,
                "message": f"Failed to update subscription status - board is archived",
                "guidance": "Closed boards cannot be edited. You must unarchive the board first.",
                "suggestion": "Use TRELLO_UPDATE_BOARDS_CLOSED_BY_ID_BOARD to unarchive the board first."
            }
        else:
            return {
                "successful": False,
                "error": f"Failed to update subscription status: {error_message}",
                "action": "update_board_subscription",
                "board_id": id_board,
                "message": f"Failed to update subscription status for board {id_board}"
            }


# -------------------- NOTIFICATION BOARD FIELD TOOLS --------------------

@mcp.tool(
    "TRELLO_GET_NOTIFICATIONS_BOARD_BY_ID_NOTIFICATION_BY_FIELD",
    description="Get notification's board field. Retrieves a specific, valid field from the board associated with a trello notification.",
)
def TRELLO_GET_NOTIFICATIONS_BOARD_BY_ID_NOTIFICATION_BY_FIELD(
    id_notification: Annotated[str, "The ID of the notification to get the board field for."],
    field: Annotated[str, "The specific field to retrieve from the board (e.g., name, desc, url, closed, idOrganization)."]
):
    """Get notification's board field. Retrieves a specific, valid field from the board associated with a trello notification."""
    err = _validate_required({"id_notification": id_notification, "field": field}, ["id_notification", "field"])
    if err:
        return err
    
    try:
        # Get specific field from board for the notification
        endpoint = f"/notifications/{id_notification}/board"
        
        # Build query parameters
        params = {
            "fields": field
        }
        
        # Make the API request
        result = trello_request("GET", endpoint, params=params)
        
        if not isinstance(result, dict):
            return {
                "successful": False,
                "error": "Invalid board data received",
                "action": "get_notification_board_field",
                "notification_id": id_notification,
                "field": field,
                "message": f"Failed to retrieve board field '{field}' for notification {id_notification}"
            }
        
        # Extract the specific field value
        field_value = result.get(field)
        
        return {
            "successful": True,
            "data": {field: field_value},
            "action": "get_notification_board_field",
            "notification_id": id_notification,
            "field": field,
            "field_value": field_value,
            "message": f"Successfully retrieved board field '{field}' for notification {id_notification}",
            "board_field": field_value
        }
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve notification board field: {str(e)}",
            "action": "get_notification_board_field",
            "notification_id": id_notification,
            "field": field,
            "message": f"Failed to retrieve board field '{field}' for notification {id_notification}"
        }


# -------------------- NOTIFICATION DETAILS TOOLS --------------------

@mcp.tool(
    "TRELLO_GET_NOTIFICATIONS_BY_ID_NOTIFICATION",
    description="Get notification by ID. Retrieves a specific trello notification by its id, optionally including related entities and specific fields for the notification and its related entities.",
)
def TRELLO_GET_NOTIFICATIONS_BY_ID_NOTIFICATION(
    id_notification: Annotated[str, "The ID of the notification to retrieve."],
    board: Annotated[str | None, "Whether to include board information."] = None,
    board_fields: Annotated[str, "The fields to retrieve from the board. Defaults to name."] = "name",
    card: Annotated[str | None, "Whether to include card information."] = None,
    card_fields: Annotated[str, "The fields to retrieve from the card. Defaults to name."] = "name",
    display: Annotated[str | None, "Whether to include display information."] = None,
    entities: Annotated[str | None, "Whether to include entities in the response."] = None,
    fields: Annotated[str, "The fields to retrieve from the notification. Defaults to all."] = "all",
    list: Annotated[str | None, "Whether to include list information."] = None,
    member: Annotated[str | None, "Whether to include member information."] = None,
    member_creator: Annotated[str | None, "Whether to include member creator information."] = None,
    member_creator_fields: Annotated[str, "The fields to retrieve from member creators. Defaults to avatarHash, fullName, initials and username."] = "avatarHash,fullName,initials,username",
    member_fields: Annotated[str, "The fields to retrieve from members. Defaults to avatarHash, fullName, initials and username."] = "avatarHash,fullName,initials,username",
    organization: Annotated[str | None, "Whether to include organization information."] = None,
    organization_fields: Annotated[str, "The fields to retrieve from the organization. Defaults to displayName."] = "displayName"
):
    """Get notification by ID. Retrieves a specific trello notification by its id, optionally including related entities and specific fields for the notification and its related entities."""
    err = _validate_required({"id_notification": id_notification}, ["id_notification"])
    if err:
        return err
    
    try:
        # Get notification by ID
        endpoint = f"/notifications/{id_notification}"
        
        # Build query parameters
        params = {}
        if board is not None:
            params["board"] = board
        if board_fields is not None:
            params["board_fields"] = board_fields
        if card is not None:
            params["card"] = card
        if card_fields is not None:
            params["card_fields"] = card_fields
        if display is not None:
            params["display"] = display
        if entities is not None:
            params["entities"] = entities
        if fields is not None:
            params["fields"] = fields
        if list is not None:
            params["list"] = list
        if member is not None:
            params["member"] = member
        if member_creator is not None:
            params["memberCreator"] = member_creator
        if member_creator_fields is not None:
            params["memberCreator_fields"] = member_creator_fields
        if member_fields is not None:
            params["member_fields"] = member_fields
        if organization is not None:
            params["organization"] = organization
        if organization_fields is not None:
            params["organization_fields"] = organization_fields
        
        # Make the API request
        result = trello_request("GET", endpoint, params=params)
        
        if not isinstance(result, dict):
            return {
                "successful": False,
                "error": "Invalid notification data received",
                "action": "get_notification",
                "notification_id": id_notification,
                "message": f"Failed to retrieve notification {id_notification}"
            }
        
        # Extract key information
        notification_type = result.get("type")
        notification_date = result.get("date")
        notification_read = result.get("unread")
        notification_data = result.get("data", {})
        
        response = {
            "successful": True,
            "data": result,
            "action": "get_notification",
            "notification_id": id_notification,
            "notification_type": notification_type,
            "notification_date": notification_date,
            "notification_read": not notification_read if notification_read is not None else None,
            "message": f"Successfully retrieved notification {id_notification}",
            "notification": result
        }
        
        # Add related entities if included
        if "board" in result:
            response["board"] = result["board"]
            response["board_name"] = result["board"].get("name") if isinstance(result["board"], dict) else None
        
        if "card" in result:
            response["card"] = result["card"]
            response["card_name"] = result["card"].get("name") if isinstance(result["card"], dict) else None
        
        if "list" in result:
            response["list"] = result["list"]
            response["list_name"] = result["list"].get("name") if isinstance(result["list"], dict) else None
        
        if "member" in result:
            response["member"] = result["member"]
            response["member_name"] = result["member"].get("fullName") if isinstance(result["member"], dict) else None
        
        if "memberCreator" in result:
            response["member_creator"] = result["memberCreator"]
            response["member_creator_name"] = result["memberCreator"].get("fullName") if isinstance(result["memberCreator"], dict) else None
        
        if "organization" in result:
            response["organization"] = result["organization"]
            response["organization_name"] = result["organization"].get("displayName") if isinstance(result["organization"], dict) else None
        
        # Add helpful information
        response["note"] = f"Retrieved notification of type '{notification_type}' with comprehensive entity details"
        
        return response
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve notification: {str(e)}",
            "action": "get_notification",
            "notification_id": id_notification,
            "message": f"Failed to retrieve notification {id_notification}"
        }


@mcp.tool(
    "TRELLO_GET_NOTIFICATIONS_BY_ID_NOTIFICATION_BY_FIELD",
    description="Get a notification field. Retrieves a specific field from a trello notification.",
)
def TRELLO_GET_NOTIFICATIONS_BY_ID_NOTIFICATION_BY_FIELD(
    id_notification: Annotated[str, "The ID of the notification to get the field from."],
    field: Annotated[str, "The specific field to retrieve from the notification (e.g., id, type, date, unread, data)."]
):
    """Get a notification field. Retrieves a specific field from a trello notification."""
    err = _validate_required({"id_notification": id_notification, "field": field}, ["id_notification", "field"])
    if err:
        return err
    
    try:
        # Get specific field from notification
        endpoint = f"/notifications/{id_notification}"
        
        # Build query parameters
        params = {
            "fields": field
        }
        
        # Make the API request
        result = trello_request("GET", endpoint, params=params)
        
        if not isinstance(result, dict):
            return {
                "successful": False,
                "error": "Invalid notification data received",
                "action": "get_notification_field",
                "notification_id": id_notification,
                "field": field,
                "message": f"Failed to retrieve notification field '{field}' for notification {id_notification}"
            }
        
        # Extract the specific field value
        field_value = result.get(field)
        
        return {
            "successful": True,
            "data": {field: field_value},
            "action": "get_notification_field",
            "notification_id": id_notification,
            "field": field,
            "field_value": field_value,
            "message": f"Successfully retrieved notification field '{field}' for notification {id_notification}",
            "notification_field": field_value
        }
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve notification field: {str(e)}",
            "action": "get_notification_field",
            "notification_id": id_notification,
            "field": field,
            "message": f"Failed to retrieve notification field '{field}' for notification {id_notification}"
        }


@mcp.tool(
    "TRELLO_GET_NOTIFICATIONS_DISPLAY_BY_ID_NOTIFICATION",
    description="Get notification display by id. Retrieves the information needed to display an existing trello notification, identified by its id, without altering the notification or fetching its complete metadata.",
)
def TRELLO_GET_NOTIFICATIONS_DISPLAY_BY_ID_NOTIFICATION(
    id_notification: Annotated[str, "The ID of the notification to get display information for."]
):
    """Get notification display by id. Retrieves the information needed to display an existing trello notification, identified by its id, without altering the notification or fetching its complete metadata."""
    err = _validate_required({"id_notification": id_notification}, ["id_notification"])
    if err:
        return err
    
    try:
        # Get notification display information
        endpoint = f"/notifications/{id_notification}/display"
        
        # Make the API request
        result = trello_request("GET", endpoint)
        
        if not isinstance(result, dict):
            return {
                "successful": False,
                "error": "Invalid notification display data received",
                "action": "get_notification_display",
                "notification_id": id_notification,
                "message": f"Failed to retrieve display information for notification {id_notification}"
            }
        
        # Extract key display information
        notification_type = result.get("type")
        notification_text = result.get("text")
        notification_date = result.get("date")
        notification_unread = result.get("unread")
        notification_data = result.get("data", {})
        
        response = {
            "successful": True,
            "data": result,
            "action": "get_notification_display",
            "notification_id": id_notification,
            "notification_type": notification_type,
            "notification_text": notification_text,
            "notification_date": notification_date,
            "notification_unread": notification_unread,
            "message": f"Successfully retrieved display information for notification {id_notification}",
            "display_info": result
        }
        
        # Add helpful display context
        if notification_text:
            response["note"] = f"Display text: {notification_text}"
        elif notification_type:
            response["note"] = f"Notification type: {notification_type}"
        else:
            response["note"] = f"Display information for notification {id_notification}"
        
        return response
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve notification display: {str(e)}",
            "action": "get_notification_display",
            "notification_id": id_notification,
            "message": f"Failed to retrieve display information for notification {id_notification}"
        }


@mcp.tool(
    "TRELLO_GET_NOTIFICATIONS_MEMBER_BY_ID_NOTIFICATION",
    description="Get notification member by id. Fetches details of the member (not the notification content itself) associated with a specific trello notification id.",
)
def TRELLO_GET_NOTIFICATIONS_MEMBER_BY_ID_NOTIFICATION(
    id_notification: Annotated[str, "The ID of the notification to get the member for."],
    fields: Annotated[str, "The fields to retrieve from the member (e.g., id, username, fullName, initials, avatarHash, bio, bioData, confirmed, memberType, url, gravatarHash, uploadedAvatarHash, prefs, trophies, uploadedAvatarId, premiumFeatures, idBoards, idOrganizations, loginTypes, newEmail, idEnterprisesDeactivated, limits, idTags, avatarUrl, email, idBoardsPinned, ixUpdate, idEnterprisesAdmin, limits, nonPublic, nonPublicAvailable, products, idBoardsPinned, ixUpdate, idEnterprisesAdmin, limits, nonPublic, nonPublicAvailable, products). Defaults to all."] = "all"
):
    """Get notification member by id. Fetches details of the member (not the notification content itself) associated with a specific trello notification id."""
    err = _validate_required({"id_notification": id_notification}, ["id_notification"])
    if err:
        return err
    
    try:
        # Get member for the notification
        endpoint = f"/notifications/{id_notification}/member"
        
        # Build query parameters
        params = {}
        if fields is not None:
            params["fields"] = fields
        
        # Make the API request
        result = trello_request("GET", endpoint, params=params)
        
        if not isinstance(result, dict):
            return {
                "successful": False,
                "error": "Invalid member data received",
                "action": "get_notification_member",
                "notification_id": id_notification,
                "message": f"Failed to retrieve member for notification {id_notification}"
            }
        
        # Extract key information
        member_id = result.get("id")
        username = result.get("username")
        full_name = result.get("fullName")
        initials = result.get("initials")
        avatar_hash = result.get("avatarHash")
        bio = result.get("bio")
        confirmed = result.get("confirmed")
        member_type = result.get("memberType")
        url = result.get("url")
        
        response = {
            "successful": True,
            "data": result,
            "action": "get_notification_member",
            "notification_id": id_notification,
            "member_id": member_id,
            "username": username,
            "full_name": full_name,
            "initials": initials,
            "avatar_hash": avatar_hash,
            "bio": bio,
            "confirmed": confirmed,
            "member_type": member_type,
            "url": url,
            "message": f"Successfully retrieved member for notification {id_notification}",
            "member": result
        }
        
        # Add helpful information
        if full_name:
            response["note"] = f"Member '{full_name}' ({username}) associated with notification {id_notification}"
        elif username:
            response["note"] = f"Member '{username}' associated with notification {id_notification}"
        else:
            response["note"] = f"Member {member_id} associated with notification {id_notification}"
        
        return response
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve notification member: {str(e)}",
            "action": "get_notification_member",
            "notification_id": id_notification,
            "message": f"Failed to retrieve member for notification {id_notification}"
        }


@mcp.tool(
    "TRELLO_GET_ORGANIZATIONS_ACTIONS_BY_ID_ORG",
    description="Get organization actions by ID. Retrieves a log of actions (e.g., card creations, list movements, comments) for a specified trello organization, filterable by type, date range, and models; `idorg` must be a valid organization id/name, and `page` * `limit` must be < 1000.",
)
def TRELLO_GET_ORGANIZATIONS_ACTIONS_BY_ID_ORG(
    idOrg: Annotated[str, "The ID or name of the organization to get actions for."],
    before: Annotated[Optional[str], "An action ID. Only return actions before this action."] = None,
    display: Annotated[Optional[str], "Display type for the actions."] = None,
    entities: Annotated[Optional[str], "Whether to include entities in the response."] = None,
    fields: Annotated[Optional[str], "Fields to return. Defaults to all."] = "all",
    filter: Annotated[Optional[str], "Filter for specific action types. Defaults to all."] = "all",
    format: Annotated[Optional[str], "Format of the response. Defaults to list."] = "list",
    idModels: Annotated[Optional[str], "Comma-separated list of model IDs to filter by."] = None,
    limit: Annotated[Optional[str], "Maximum number of actions to return. Defaults to 50."] = "50",
    member: Annotated[Optional[str], "Filter actions by member ID."] = None,
    memberCreator: Annotated[Optional[str], "Filter actions by member creator ID."] = None,
    memberCreator_fields: Annotated[Optional[str], "Fields to return for member creator. Defaults to avatarHash, fullName, initials and username."] = "avatarHash,fullName,initials,username",
    member_fields: Annotated[Optional[str], "Fields to return for member. Defaults to avatarHash, fullName, initials and username."] = "avatarHash,fullName,initials,username",
    page: Annotated[Optional[str], "Page number for pagination. Defaults to 0."] = "0",
    since: Annotated[Optional[str], "Only return actions since this date (ISO 8601 format)."] = None
):
    """Get organization actions by ID. Retrieves a log of actions (e.g., card creations, list movements, comments) for a specified trello organization, filterable by type, date range, and models; `idorg` must be a valid organization id/name, and `page` * `limit` must be < 1000."""
    err = _validate_required({"idOrg": idOrg}, ["idOrg"])
    if err:
        return err
    
    # Validate page * limit < 1000
    try:
        page_num = int(page) if page else 0
        limit_num = int(limit) if limit else 50
        if page_num * limit_num >= 1000:
            return {
                "successful": False,
                "error": "page * limit must be < 1000",
                "action": "get_organization_actions",
                "organization_id": idOrg,
                "message": f"Invalid pagination: page {page_num} * limit {limit_num} = {page_num * limit_num} >= 1000"
            }
    except ValueError:
        return {
            "successful": False,
            "error": "Invalid page or limit parameter",
            "action": "get_organization_actions",
            "organization_id": idOrg,
            "message": "Page and limit must be valid integers"
        }
    
    # Build the endpoint
    endpoint = f"/organizations/{idOrg}/actions"
    
    # Build query parameters
    params = {}
    if before is not None:
        params["before"] = before
    if display is not None:
        params["display"] = display
    if entities is not None:
        params["entities"] = entities
    if fields is not None and fields.strip() and fields.lower() != "all":
        params["fields"] = fields
    if filter is not None and filter.strip() and filter.lower() != "all":
        params["filter"] = filter
    if format is not None and format.strip() and format.lower() != "list":
        params["format"] = format
    if idModels is not None:
        params["idModels"] = idModels
    if limit is not None:
        params["limit"] = limit
    if member is not None:
        params["member"] = member
    if memberCreator is not None:
        params["memberCreator"] = memberCreator
    if memberCreator_fields is not None:
        params["memberCreator_fields"] = memberCreator_fields
    if member_fields is not None:
        params["member_fields"] = member_fields
    if page is not None:
        params["page"] = page
    if since is not None:
        params["since"] = since
    
    try:
        # Make the API request
        result = trello_request("GET", endpoint, params=params)
        
        if not isinstance(result, (list, dict)):
            return {
                "successful": False,
                "error": "Invalid actions data received",
                "action": "get_organization_actions",
                "organization_id": idOrg,
                "message": f"Failed to retrieve actions for organization {idOrg}"
            }
        
        # Handle both list and dict responses
        actions_data = result if isinstance(result, list) else result.get("data", result)
        
        response = {
            "successful": True,
            "data": actions_data,
            "action": "get_organization_actions",
            "organization_id": idOrg,
            "page": page_num,
            "limit": limit_num,
            "total_actions": len(actions_data) if isinstance(actions_data, list) else 1,
            "message": f"Successfully retrieved {len(actions_data) if isinstance(actions_data, list) else 1} action(s) for organization {idOrg}"
        }
        
        # Add filter information if provided
        if filter and filter.strip() and filter.lower() != "all":
            response["filter"] = filter
        if since:
            response["since"] = since
        if before:
            response["before"] = before
        
        return response
        
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve organization actions: {str(e)}",
            "action": "get_organization_actions",
            "organization_id": idOrg,
            "message": f"Failed to retrieve actions for organization {idOrg}"
        }


@mcp.tool(
    "TRELLO_GET_ORGANIZATIONS_BOARDS_BY_ID_ORG",
    description="Get organization boards. Fetches boards for a trello organization, specified by its id or name, with options to filter and customize returned data.",
)
def TRELLO_GET_ORGANIZATIONS_BOARDS_BY_ID_ORG(
    idOrg: Annotated[str, "The ID or name of the organization to get boards for."],
    action_fields: Annotated[Optional[str], "Fields to return for actions. Defaults to all."] = "all",
    actions: Annotated[Optional[str], "Whether to include actions. Defaults to none."] = "none",
    actions_entities: Annotated[Optional[str], "Whether to include action entities."] = None,
    actions_format: Annotated[Optional[str], "Format for actions. Defaults to list."] = "list",
    actions_limit: Annotated[Optional[str], "Limit for number of actions. Defaults to 5."] = "5",
    actions_since: Annotated[Optional[str], "Only return actions since this date (ISO 8601 format)."] = None,
    fields: Annotated[Optional[str], "Fields to return for boards. Defaults to all."] = "all",
    filter: Annotated[Optional[str], "Filter for specific board types. Defaults to all."] = "all",
    lists: Annotated[Optional[str], "Whether to include lists. Defaults to none."] = "none",
    memberships: Annotated[Optional[str], "Whether to include memberships. Defaults to none."] = "none",
    organization: Annotated[Optional[str], "Whether to include organization info."] = None,
    organization_fields: Annotated[Optional[str], "Fields to return for organization. Defaults to name and displayName."] = "name,displayName"
):
    """Get organization boards. Fetches boards for a trello organization, specified by its id or name, with options to filter and customize returned data."""
    err = _validate_required({"idOrg": idOrg}, ["idOrg"])
    if err:
        return err
    
    # Build the endpoint
    endpoint = f"/organizations/{idOrg}/boards"
    
    # Build query parameters
    params = {}
    if action_fields is not None and action_fields.strip() and action_fields.lower() != "all":
        params["action_fields"] = action_fields
    if actions is not None and actions.strip() and actions.lower() != "none":
        params["actions"] = actions
    if actions_entities is not None:
        params["actions_entities"] = actions_entities
    if actions_format is not None and actions_format.strip() and actions_format.lower() != "list":
        params["actions_format"] = actions_format
    if actions_limit is not None:
        params["actions_limit"] = actions_limit
    if actions_since is not None:
        params["actions_since"] = actions_since
    if fields is not None and fields.strip() and fields.lower() != "all":
        params["fields"] = fields
    if filter is not None and filter.strip() and filter.lower() != "all":
        params["filter"] = filter
    if lists is not None and lists.strip() and lists.lower() != "none":
        params["lists"] = lists
    if memberships is not None and memberships.strip() and memberships.lower() != "none":
        params["memberships"] = memberships
    if organization is not None:
        params["organization"] = organization
    if organization_fields is not None:
        params["organization_fields"] = organization_fields
    
    try:
        # Make the API request
        result = trello_request("GET", endpoint, params=params)
        
        if not isinstance(result, (list, dict)):
            return {
                "successful": False,
                "error": "Invalid boards data received",
                "action": "get_organization_boards",
                "organization_id": idOrg,
                "message": f"Failed to retrieve boards for organization {idOrg}"
            }
        
        # Handle both list and dict responses
        boards_data = result if isinstance(result, list) else result.get("data", result)
        
        response = {
            "successful": True,
            "data": boards_data,
            "action": "get_organization_boards",
            "organization_id": idOrg,
            "total_boards": len(boards_data) if isinstance(boards_data, list) else 1,
            "message": f"Successfully retrieved {len(boards_data) if isinstance(boards_data, list) else 1} board(s) for organization {idOrg}"
        }
        
        # Add filter information if provided
        if filter and filter.strip() and filter.lower() != "all":
            response["filter"] = filter
        if actions and actions.strip() and actions.lower() != "none":
            response["actions_included"] = True
            response["actions_limit"] = actions_limit
        if lists and lists.strip() and lists.lower() != "none":
            response["lists_included"] = True
        if memberships and memberships.strip() and memberships.lower() != "none":
            response["memberships_included"] = True
        
        return response
        
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve organization boards: {str(e)}",
            "action": "get_organization_boards",
            "organization_id": idOrg,
            "message": f"Failed to retrieve boards for organization {idOrg}"
        }


@mcp.tool(
    "TRELLO_GET_ORGANIZATIONS_BOARDS_BY_ID_ORG_BY_FILTER",
    description="Get organization boards by filter. Fetches a list of boards belonging to a specific trello organization, filtered by a given criterion.",
)
def TRELLO_GET_ORGANIZATIONS_BOARDS_BY_ID_ORG_BY_FILTER(
    idOrg: Annotated[str, "The ID or name of the organization to get boards for."],
    filter: Annotated[str, "The filter criterion to apply to the boards (e.g., 'open', 'closed', 'all', 'starred', 'members', 'organization', 'public', 'private')."]
):
    """Get organization boards by filter. Fetches a list of boards belonging to a specific trello organization, filtered by a given criterion."""
    err = _validate_required({"idOrg": idOrg, "filter": filter}, ["idOrg", "filter"])
    if err:
        return err
    
    # Build the endpoint
    endpoint = f"/organizations/{idOrg}/boards"
    
    # Build query parameters with the filter
    params = {
        "filter": filter
    }
    
    try:
        # Make the API request
        result = trello_request("GET", endpoint, params=params)
        
        if not isinstance(result, (list, dict)):
            return {
                "successful": False,
                "error": "Invalid boards data received",
                "action": "get_organization_boards_by_filter",
                "organization_id": idOrg,
                "filter": filter,
                "message": f"Failed to retrieve filtered boards for organization {idOrg}"
            }
        
        # Handle both list and dict responses
        boards_data = result if isinstance(result, list) else result.get("data", result)
        
        response = {
            "successful": True,
            "data": boards_data,
            "action": "get_organization_boards_by_filter",
            "organization_id": idOrg,
            "filter": filter,
            "total_boards": len(boards_data) if isinstance(boards_data, list) else 1,
            "message": f"Successfully retrieved {len(boards_data) if isinstance(boards_data, list) else 1} board(s) for organization {idOrg} with filter '{filter}'"
        }
        
        return response
        
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve filtered organization boards: {str(e)}",
            "action": "get_organization_boards_by_filter",
            "organization_id": idOrg,
            "filter": filter,
            "message": f"Failed to retrieve boards for organization {idOrg} with filter '{filter}'"
        }


@mcp.tool(
    "TRELLO_GET_ORGANIZATIONS_BY_ID_ORG",
    description="Get organization by ID. Retrieves detailed information about a specific trello organization, including optional related resources like members, boards, and actions, using its id or unique name.",
)
def TRELLO_GET_ORGANIZATIONS_BY_ID_ORG(
    idOrg: Annotated[str, "The ID or unique name of the organization to retrieve."],
    action_fields: Annotated[Optional[str], "Fields to return for actions. Defaults to all."] = "all",
    actions: Annotated[Optional[str], "Whether to include actions. Defaults to none."] = "none",
    actions_display: Annotated[Optional[str], "Whether to include action display information."] = None,
    actions_entities: Annotated[Optional[str], "Whether to include action entities."] = None,
    actions_limit: Annotated[Optional[str], "Limit for number of actions. Defaults to 50."] = "50",
    board_action_fields: Annotated[Optional[str], "Fields to return for board actions. Defaults to all."] = "all",
    board_actions: Annotated[Optional[str], "Whether to include board actions."] = None,
    board_actions_display: Annotated[Optional[str], "Whether to include board action display information."] = None,
    board_actions_entities: Annotated[Optional[str], "Whether to include board action entities."] = None,
    board_actions_format: Annotated[Optional[str], "Format for board actions. Defaults to list."] = "list",
    board_actions_limit: Annotated[Optional[str], "Limit for number of board actions. Defaults to 50."] = "50",
    board_actions_since: Annotated[Optional[str], "Only return board actions since this date (ISO 8601 format)."] = None,
    board_fields: Annotated[Optional[str], "Fields to return for boards. Defaults to all."] = "all",
    board_lists: Annotated[Optional[str], "Whether to include board lists. Defaults to open."] = "open",
    boards: Annotated[Optional[str], "Whether to include boards. Defaults to none."] = "none",
    fields: Annotated[Optional[str], "Fields to return for organization. Defaults to name, displayName, desc, descData, url, website, logoHash, products and powerUps."] = "name,displayName,desc,descData,url,website,logoHash,products,powerUps",
    member_activity: Annotated[Optional[str], "Whether to include member activity."] = None,
    member_fields: Annotated[Optional[str], "Fields to return for members. Defaults to avatarHash, fullName, initials, username and confirmed."] = "avatarHash,fullName,initials,username,confirmed",
    members: Annotated[Optional[str], "Whether to include members. Defaults to none."] = "none",
    membersInvited: Annotated[Optional[str], "Whether to include invited members. Defaults to none."] = "none",
    membersInvited_fields: Annotated[Optional[str], "Fields to return for invited members. Defaults to avatarHash, initials, fullName and username."] = "avatarHash,initials,fullName,username",
    memberships: Annotated[Optional[str], "Whether to include memberships. Defaults to none."] = "none",
    memberships_member: Annotated[Optional[str], "Whether to include membership member information."] = None,
    memberships_member_fields: Annotated[Optional[str], "Fields to return for membership members. Defaults to fullName and username."] = "fullName,username",
    paid_account: Annotated[Optional[str], "Whether to include paid account information."] = None
):
    """Get organization by ID. Retrieves detailed information about a specific trello organization, including optional related resources like members, boards, and actions, using its id or unique name."""
    err = _validate_required({"idOrg": idOrg}, ["idOrg"])
    if err:
        return err
    
    # Build the endpoint
    endpoint = f"/organizations/{idOrg}"
    
    # Build query parameters
    params = {}
    if action_fields is not None and action_fields.strip() and action_fields.lower() != "all":
        params["action_fields"] = action_fields
    if actions is not None and actions.strip() and actions.lower() != "none":
        params["actions"] = actions
    if actions_display is not None:
        params["actions_display"] = actions_display
    if actions_entities is not None:
        params["actions_entities"] = actions_entities
    if actions_limit is not None:
        params["actions_limit"] = actions_limit
    if board_action_fields is not None and board_action_fields.strip() and board_action_fields.lower() != "all":
        params["board_action_fields"] = board_action_fields
    if board_actions is not None:
        params["board_actions"] = board_actions
    if board_actions_display is not None:
        params["board_actions_display"] = board_actions_display
    if board_actions_entities is not None:
        params["board_actions_entities"] = board_actions_entities
    if board_actions_format is not None and board_actions_format.strip() and board_actions_format.lower() != "list":
        params["board_actions_format"] = board_actions_format
    if board_actions_limit is not None:
        params["board_actions_limit"] = board_actions_limit
    if board_actions_since is not None:
        params["board_actions_since"] = board_actions_since
    if board_fields is not None and board_fields.strip() and board_fields.lower() != "all":
        params["board_fields"] = board_fields
    if board_lists is not None and board_lists.strip() and board_lists.lower() != "open":
        params["board_lists"] = board_lists
    if boards is not None and boards.strip() and boards.lower() != "none":
        params["boards"] = boards
    if fields is not None and fields.strip():
        params["fields"] = fields
    if member_activity is not None:
        params["member_activity"] = member_activity
    if member_fields is not None:
        params["member_fields"] = member_fields
    if members is not None and members.strip() and members.lower() != "none":
        params["members"] = members
    if membersInvited is not None and membersInvited.strip() and membersInvited.lower() != "none":
        params["membersInvited"] = membersInvited
    if membersInvited_fields is not None:
        params["membersInvited_fields"] = membersInvited_fields
    if memberships is not None and memberships.strip() and memberships.lower() != "none":
        params["memberships"] = memberships
    if memberships_member is not None:
        params["memberships_member"] = memberships_member
    if memberships_member_fields is not None:
        params["memberships_member_fields"] = memberships_member_fields
    if paid_account is not None:
        params["paid_account"] = paid_account
    
    try:
        # Make the API request
        result = trello_request("GET", endpoint, params=params)
        
        if not isinstance(result, dict):
            return {
                "successful": False,
                "error": "Invalid organization data received",
                "action": "get_organization_by_id",
                "organization_id": idOrg,
                "message": f"Failed to retrieve organization {idOrg}"
            }
        
        # Extract key organization information
        org_id = result.get("id")
        org_name = result.get("name")
        display_name = result.get("displayName")
        description = result.get("desc")
        url = result.get("url")
        website = result.get("website")
        logo_hash = result.get("logoHash")
        products = result.get("products", [])
        power_ups = result.get("powerUps", [])
        
        response = {
            "successful": True,
            "data": result,
            "action": "get_organization_by_id",
            "organization_id": org_id,
            "organization_name": org_name,
            "display_name": display_name,
            "description": description,
            "url": url,
            "website": website,
            "logo_hash": logo_hash,
            "products_count": len(products) if isinstance(products, list) else 0,
            "power_ups_count": len(power_ups) if isinstance(power_ups, list) else 0,
            "message": f"Successfully retrieved organization {org_name or idOrg}"
        }
        
        # Add information about included resources
        if actions and actions.strip() and actions.lower() != "none":
            response["actions_included"] = True
            response["actions_limit"] = actions_limit
        if boards and boards.strip() and boards.lower() != "none":
            response["boards_included"] = True
        if members and members.strip() and members.lower() != "none":
            response["members_included"] = True
        if membersInvited and membersInvited.strip() and membersInvited.lower() != "none":
            response["invited_members_included"] = True
        if memberships and memberships.strip() and memberships.lower() != "none":
            response["memberships_included"] = True
        
        return response
        
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve organization: {str(e)}",
            "action": "get_organization_by_id",
            "organization_id": idOrg,
            "message": f"Failed to retrieve organization {idOrg}"
        }


@mcp.tool(
    "TRELLO_GET_ORGANIZATIONS_BY_ID_ORG_BY_FIELD",
    description="Get organization field by id. Retrieves the value of a single specified `field` for a trello organization `idorg`, ideal for efficiently fetching a specific piece of information without loading the full organization details.",
)
def TRELLO_GET_ORGANIZATIONS_BY_ID_ORG_BY_FIELD(
    idOrg: Annotated[str, "The ID or unique name of the organization to retrieve the field from."],
    field: Annotated[str, "The specific field to retrieve from the organization (e.g., 'name', 'displayName', 'desc', 'url', 'website', 'logoHash', 'id', 'descData', 'products', 'powerUps', 'prefs', 'premiumFeatures', 'billableMemberCount', 'idTags', 'dateLastActivity', 'dateLastView', 'idBoards', 'invited', 'invitations', 'memberships', 'pinned', 'url', 'website', 'logoHash', 'products', 'powerUps', 'prefs', 'premiumFeatures', 'billableMemberCount', 'idTags', 'dateLastActivity', 'dateLastView', 'idBoards', 'invited', 'invitations', 'memberships', 'pinned')."]
):
    """Get organization field by id. Retrieves the value of a single specified `field` for a trello organization `idorg`, ideal for efficiently fetching a specific piece of information without loading the full organization details."""
    err = _validate_required({"idOrg": idOrg, "field": field}, ["idOrg", "field"])
    if err:
        return err
    
    # Build the endpoint
    endpoint = f"/organizations/{idOrg}/{field}"
    
    try:
        # Make the API request
        result = trello_request("GET", endpoint)
        
        # The result could be various types depending on the field
        field_value = result
        
        response = {
            "successful": True,
            "data": {
                "field": field,
                "value": field_value
            },
            "action": "get_organization_field",
            "organization_id": idOrg,
            "field": field,
            "field_value": field_value,
            "message": f"Successfully retrieved field '{field}' for organization {idOrg}"
        }
        
        # Add helpful information based on field type
        if isinstance(field_value, str):
            response["field_type"] = "string"
            response["field_length"] = len(field_value)
        elif isinstance(field_value, (int, float)):
            response["field_type"] = "number"
        elif isinstance(field_value, bool):
            response["field_type"] = "boolean"
        elif isinstance(field_value, list):
            response["field_type"] = "array"
            response["field_length"] = len(field_value)
        elif isinstance(field_value, dict):
            response["field_type"] = "object"
            response["field_keys"] = list(field_value.keys()) if field_value else []
        else:
            response["field_type"] = "unknown"
        
        return response
        
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve organization field: {str(e)}",
            "action": "get_organization_field",
            "organization_id": idOrg,
            "field": field,
            "message": f"Failed to retrieve field '{field}' for organization {idOrg}"
        }


@mcp.tool(
    "TRELLO_GET_ORGANIZATIONS_DELTAS_BY_ID_ORG",
    description="Get organization deltas by id. Retrieves a log of recent modifications (deltas) for a trello organization, filterable by tags and supporting incremental fetching via an update index.",
)
def TRELLO_GET_ORGANIZATIONS_DELTAS_BY_ID_ORG(
    idOrg: Annotated[str, "The ID or unique name of the organization to get deltas for."],
    ixLastUpdate: Annotated[str, "The index of the last update to start fetching from (for incremental updates). Use '0' for the first request."],
    tags: Annotated[str, "Comma-separated list of tags to filter deltas by (e.g., 'board,card,list,member,action'). Use 'all' to get all types of deltas."]
):
    """Get organization deltas by id. Retrieves a log of recent modifications (deltas) for a trello organization, filterable by tags and supporting incremental fetching via an update index."""
    err = _validate_required({"idOrg": idOrg, "ixLastUpdate": ixLastUpdate, "tags": tags}, ["idOrg", "ixLastUpdate", "tags"])
    if err:
        return err
    
    # Validate ixLastUpdate is a valid number
    try:
        update_index = int(ixLastUpdate)
        if update_index < 0:
            return {
                "successful": False,
                "error": "ixLastUpdate must be a non-negative integer",
                "action": "get_organization_deltas",
                "organization_id": idOrg,
                "message": "ixLastUpdate must be 0 or greater"
            }
    except ValueError:
        return {
            "successful": False,
            "error": "ixLastUpdate must be a valid integer",
            "action": "get_organization_deltas",
            "organization_id": idOrg,
            "message": "ixLastUpdate must be a number (use '0' for first request)"
        }
    
    # Build the endpoint
    endpoint = f"/organizations/{idOrg}/deltas"
    
    # Build query parameters
    params = {
        "ixLastUpdate": ixLastUpdate,
        "tags": tags
    }
    
    try:
        # Make the API request
        result = trello_request("GET", endpoint, params=params)
        
        if not isinstance(result, (list, dict)):
            return {
                "successful": False,
                "error": "Invalid deltas data received",
                "action": "get_organization_deltas",
                "organization_id": idOrg,
                "message": f"Failed to retrieve deltas for organization {idOrg}"
            }
        
        # Handle both list and dict responses
        deltas_data = result if isinstance(result, list) else result.get("data", result)
        
        response = {
            "successful": True,
            "data": deltas_data,
            "action": "get_organization_deltas",
            "organization_id": idOrg,
            "ixLastUpdate": update_index,
            "tags": tags,
            "total_deltas": len(deltas_data) if isinstance(deltas_data, list) else 1,
            "message": f"Successfully retrieved {len(deltas_data) if isinstance(deltas_data, list) else 1} delta(s) for organization {idOrg}"
        }
        
        # Add helpful information about the deltas
        if isinstance(deltas_data, list) and deltas_data:
            # Extract unique delta types if available
            delta_types = set()
            for delta in deltas_data:
                if isinstance(delta, dict) and "type" in delta:
                    delta_types.add(delta["type"])
            if delta_types:
                response["delta_types"] = list(delta_types)
        
        return response
        
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve organization deltas: {str(e)}",
            "action": "get_organization_deltas",
            "organization_id": idOrg,
            "message": f"Failed to retrieve deltas for organization {idOrg}"
        }


@mcp.tool(
    "TRELLO_GET_ORGANIZATIONS_MEMBERS_BY_ID_ORG",
    description="Retrieve organization members by id. Retrieves members of a trello organization (specified by id or name), with an option to include member activity if the organization is premium.",
)
def TRELLO_GET_ORGANIZATIONS_MEMBERS_BY_ID_ORG(
    idOrg: Annotated[str, "The ID or unique name of the organization to get members for."],
    activity: Annotated[Optional[str], "Whether to include member activity (only available for premium organizations)."] = None,
    fields: Annotated[Optional[str], "Fields to return for members. Defaults to fullName and username."] = "fullName,username",
    filter: Annotated[Optional[str], "Filter for member types. Defaults to normal."] = "normal"
):
    """Retrieve organization members by id. Retrieves members of a trello organization (specified by id or name), with an option to include member activity if the organization is premium."""
    err = _validate_required({"idOrg": idOrg}, ["idOrg"])
    if err:
        return err
    
    # Build the endpoint
    endpoint = f"/organizations/{idOrg}/members"
    
    # Build query parameters
    params = {}
    if activity is not None:
        params["activity"] = activity
    if fields is not None and fields.strip():
        params["fields"] = fields
    if filter is not None and filter.strip() and filter.lower() != "normal":
        params["filter"] = filter
    
    try:
        # Make the API request
        result = trello_request("GET", endpoint, params=params)
        
        if not isinstance(result, (list, dict)):
            return {
                "successful": False,
                "error": "Invalid members data received",
                "action": "get_organization_members",
                "organization_id": idOrg,
                "message": f"Failed to retrieve members for organization {idOrg}"
            }
        
        # Handle both list and dict responses
        members_data = result if isinstance(result, list) else result.get("data", result)
        
        response = {
            "successful": True,
            "data": members_data,
            "action": "get_organization_members",
            "organization_id": idOrg,
            "total_members": len(members_data) if isinstance(members_data, list) else 1,
            "message": f"Successfully retrieved {len(members_data) if isinstance(members_data, list) else 1} member(s) for organization {idOrg}"
        }
        
        # Add filter information if provided
        if filter and filter.strip() and filter.lower() != "normal":
            response["filter"] = filter
        if activity and activity.strip():
            response["activity_included"] = True
        
        # Extract member information for easier access
        if isinstance(members_data, list) and members_data:
            member_ids = []
            member_usernames = []
            member_names = []
            
            for member in members_data:
                if isinstance(member, dict):
                    if "id" in member:
                        member_ids.append(member["id"])
                    if "username" in member:
                        member_usernames.append(member["username"])
                    if "fullName" in member:
                        member_names.append(member["fullName"])
            
            if member_ids:
                response["member_ids"] = member_ids
            if member_usernames:
                response["member_usernames"] = member_usernames
            if member_names:
                response["member_names"] = member_names
        
        return response
        
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve organization members: {str(e)}",
            "action": "get_organization_members",
            "organization_id": idOrg,
            "message": f"Failed to retrieve members for organization {idOrg}"
        }


@mcp.tool(
    "TRELLO_GET_ORGANIZATIONS_MEMBERS_BY_ID_ORG_BY_FILTER",
    description="Get organization members by filter. Fetches members of a specified trello organization using a filter like 'all', 'normal', 'admins', or 'owners'.",
)
def TRELLO_GET_ORGANIZATIONS_MEMBERS_BY_ID_ORG_BY_FILTER(
    idOrg: Annotated[str, "The ID or unique name of the organization to get members for."],
    filter: Annotated[str, "The filter to apply to members (e.g., 'all', 'normal', 'admins', 'owners')."]
):
    """Get organization members by filter. Fetches members of a specified trello organization using a filter like 'all', 'normal', 'admins', or 'owners'."""
    err = _validate_required({"idOrg": idOrg, "filter": filter}, ["idOrg", "filter"])
    if err:
        return err
    
    # Build the endpoint
    endpoint = f"/organizations/{idOrg}/members"
    
    # Build query parameters with the filter
    params = {
        "filter": filter
    }
    
    try:
        # Make the API request
        result = trello_request("GET", endpoint, params=params)
        
        if not isinstance(result, (list, dict)):
            return {
                "successful": False,
                "error": "Invalid members data received",
                "action": "get_organization_members_by_filter",
                "organization_id": idOrg,
                "filter": filter,
                "message": f"Failed to retrieve filtered members for organization {idOrg}"
            }
        
        # Handle both list and dict responses
        members_data = result if isinstance(result, list) else result.get("data", result)
        
        response = {
            "successful": True,
            "data": members_data,
            "action": "get_organization_members_by_filter",
            "organization_id": idOrg,
            "filter": filter,
            "total_members": len(members_data) if isinstance(members_data, list) else 1,
            "message": f"Successfully retrieved {len(members_data) if isinstance(members_data, list) else 1} member(s) for organization {idOrg} with filter '{filter}'"
        }
        
        # Extract member information for easier access
        if isinstance(members_data, list) and members_data:
            member_ids = []
            member_usernames = []
            member_names = []
            member_types = []
            
            for member in members_data:
                if isinstance(member, dict):
                    if "id" in member:
                        member_ids.append(member["id"])
                    if "username" in member:
                        member_usernames.append(member["username"])
                    if "fullName" in member:
                        member_names.append(member["fullName"])
                    if "memberType" in member:
                        member_types.append(member["memberType"])
            
            if member_ids:
                response["member_ids"] = member_ids
            if member_usernames:
                response["member_usernames"] = member_usernames
            if member_names:
                response["member_names"] = member_names
            if member_types:
                response["member_types"] = member_types
        
        return response
        
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve filtered organization members: {str(e)}",
            "action": "get_organization_members_by_filter",
            "organization_id": idOrg,
            "filter": filter,
            "message": f"Failed to retrieve members for organization {idOrg} with filter '{filter}'"
        }


@mcp.tool(
    "TRELLO_GET_ORGANIZATIONS_MEMBERSHIPS_BY_ID_ORG",
    description="Get organization memberships. Fetches organization-level memberships for a trello organization, with options to filter members and include their details; does not return board-specific memberships.",
)
def TRELLO_GET_ORGANIZATIONS_MEMBERSHIPS_BY_ID_ORG(
    idOrg: Annotated[str, "The ID or unique name of the organization to get memberships for."],
    filter: Annotated[Optional[str], "Filter for membership types. Defaults to all."] = "all",
    member: Annotated[Optional[str], "Whether to include member details. Defaults to none."] = None,
    member_fields: Annotated[Optional[str], "Fields to return for members. Defaults to fullName and username."] = "fullName,username"
):
    """Get organization memberships. Fetches organization-level memberships for a trello organization, with options to filter members and include their details; does not return board-specific memberships."""
    err = _validate_required({"idOrg": idOrg}, ["idOrg"])
    if err:
        return err
    
    # Build the endpoint
    endpoint = f"/organizations/{idOrg}/memberships"
    
    # Build query parameters
    params = {}
    if filter is not None and filter.strip() and filter.lower() != "all":
        params["filter"] = filter
    if member is not None and member.strip():
        params["member"] = member
    if member_fields is not None and member_fields.strip():
        params["member_fields"] = member_fields
    
    try:
        # Make the API request
        result = trello_request("GET", endpoint, params=params)
        
        if not isinstance(result, (list, dict)):
            return {
                "successful": False,
                "error": "Invalid memberships data received",
                "action": "get_organization_memberships",
                "organization_id": idOrg,
                "message": f"Failed to retrieve memberships for organization {idOrg}"
            }
        
        # Handle both list and dict responses
        memberships_data = result if isinstance(result, list) else result.get("data", result)
        
        response = {
            "successful": True,
            "data": memberships_data,
            "action": "get_organization_memberships",
            "organization_id": idOrg,
            "total_memberships": len(memberships_data) if isinstance(memberships_data, list) else 1,
            "message": f"Successfully retrieved {len(memberships_data) if isinstance(memberships_data, list) else 1} membership(s) for organization {idOrg}"
        }
        
        # Add filter information if provided
        if filter and filter.strip() and filter.lower() != "all":
            response["filter"] = filter
        if member and member.strip():
            response["member_details_included"] = True
        
        # Extract membership information for easier access
        if isinstance(memberships_data, list) and memberships_data:
            membership_types = []
            member_ids = []
            member_usernames = []
            member_names = []
            
            for membership in memberships_data:
                if isinstance(membership, dict):
                    # Extract membership type
                    if "type" in membership:
                        membership_types.append(membership["type"])
                    
                    # Extract member information if available
                    if "member" in membership and isinstance(membership["member"], dict):
                        member_info = membership["member"]
                        if "id" in member_info:
                            member_ids.append(member_info["id"])
                        if "username" in member_info:
                            member_usernames.append(member_info["username"])
                        if "fullName" in member_info:
                            member_names.append(member_info["fullName"])
            
            if membership_types:
                response["membership_types"] = list(set(membership_types))
            if member_ids:
                response["member_ids"] = member_ids
            if member_usernames:
                response["member_usernames"] = member_usernames
            if member_names:
                response["member_names"] = member_names
        
        return response
        
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve organization memberships: {str(e)}",
            "action": "get_organization_memberships",
            "organization_id": idOrg,
            "message": f"Failed to retrieve memberships for organization {idOrg}"
        }


@mcp.tool(
    "TRELLO_GET_ORGANIZATIONS_MEMBERSHIPS_BY_ID_ORG_BY_ID_MEMBERSHIP",
    description="Get organization membership. Retrieves a specific membership within a trello organization, using their respective ids, to ascertain the member's role, status, or permissions.",
)
def TRELLO_GET_ORGANIZATIONS_MEMBERSHIPS_BY_ID_ORG_BY_ID_MEMBERSHIP(
    idOrg: Annotated[str, "The ID or unique name of the organization."],
    idMembership: Annotated[str, "The ID of the specific membership to retrieve."],
    member: Annotated[Optional[str], "Whether to include member details. Defaults to none."] = None,
    member_fields: Annotated[Optional[str], "Fields to return for member. Defaults to fullName and username."] = "fullName,username"
):
    """Get organization membership. Retrieves a specific membership within a trello organization, using their respective ids, to ascertain the member's role, status, or permissions."""
    err = _validate_required({"idOrg": idOrg, "idMembership": idMembership}, ["idOrg", "idMembership"])
    if err:
        return err
    
    # Build the endpoint
    endpoint = f"/organizations/{idOrg}/memberships/{idMembership}"
    
    # Build query parameters
    params = {}
    if member is not None and member.strip():
        params["member"] = member
    if member_fields is not None and member_fields.strip():
        params["member_fields"] = member_fields
    
    try:
        # Make the API request
        result = trello_request("GET", endpoint, params=params)
        
        if not isinstance(result, dict):
            return {
                "successful": False,
                "error": "Invalid membership data received",
                "action": "get_organization_membership",
                "organization_id": idOrg,
                "membership_id": idMembership,
                "message": f"Failed to retrieve membership {idMembership} for organization {idOrg}"
            }
        
        response = {
            "successful": True,
            "data": result,
            "action": "get_organization_membership",
            "organization_id": idOrg,
            "membership_id": idMembership,
            "message": f"Successfully retrieved membership {idMembership} for organization {idOrg}"
        }
        
        # Extract key membership information
        membership_type = result.get("type")
        membership_id = result.get("id")
        member_id = result.get("idMember")
        deactivated = result.get("deactivated")
        
        if membership_type:
            response["membership_type"] = membership_type
        if membership_id:
            response["membership_id"] = membership_id
        if member_id:
            response["member_id"] = member_id
        if deactivated is not None:
            response["deactivated"] = deactivated
        
        # Extract member information if available
        if "member" in result and isinstance(result["member"], dict):
            member_info = result["member"]
            member_username = member_info.get("username")
            member_full_name = member_info.get("fullName")
            member_email = member_info.get("email")
            
            if member_username:
                response["member_username"] = member_username
            if member_full_name:
                response["member_full_name"] = member_full_name
            if member_email:
                response["member_email"] = member_email
            
            response["member_details_included"] = True
        else:
            response["member_details_included"] = False
        
        # Add helpful information about the membership
        if membership_type:
            if membership_type == "admin":
                response["role_description"] = "Administrator - can manage organization settings and members"
            elif membership_type == "owner":
                response["role_description"] = "Owner - has full control over the organization"
            elif membership_type == "normal":
                response["role_description"] = "Normal member - standard organization access"
            else:
                response["role_description"] = f"Custom role: {membership_type}"
        
        return response
        
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve organization membership: {str(e)}",
            "action": "get_organization_membership",
            "organization_id": idOrg,
            "membership_id": idMembership,
            "message": f"Failed to retrieve membership {idMembership} for organization {idOrg}"
        }


@mcp.tool(
    "TRELLO_GET_ORGANIZATIONS_MEMBERS_INVITED_BY_ID_ORG",
    description="Get invited organization members. Retrieves members invited to a trello organization who have not yet accepted their invitation, returning only data for pending invitations (not active or former members) and cannot send or modify invitations.",
)
def TRELLO_GET_ORGANIZATIONS_MEMBERS_INVITED_BY_ID_ORG(
    idOrg: Annotated[str, "The ID or unique name of the organization to get invited members for."],
    fields: Annotated[Optional[str], "Fields to return for invited members. Defaults to all."] = "all"
):
    """Get invited organization members. Retrieves members invited to a trello organization who have not yet accepted their invitation, returning only data for pending invitations (not active or former members) and cannot send or modify invitations."""
    err = _validate_required({"idOrg": idOrg}, ["idOrg"])
    if err:
        return err
    
    # Build the endpoint - use memberships endpoint to get invited members
    endpoint = f"/organizations/{idOrg}/memberships"
    
    # Build query parameters
    params = {
        "filter": "all",  # Get all memberships, we'll filter for invited ones
        "member": "true"  # Include member details
    }
    if fields is not None and fields.strip() and fields.lower() != "all":
        params["member_fields"] = fields
    
    try:
        # Make the API request
        result = trello_request("GET", endpoint, params=params)
        
        if not isinstance(result, (list, dict)):
            return {
                "successful": False,
                "error": "Invalid invited members data received",
                "action": "get_invited_organization_members",
                "organization_id": idOrg,
                "message": f"Failed to retrieve invited members for organization {idOrg}"
            }
        
        # Handle both list and dict responses
        memberships_data = result if isinstance(result, list) else result.get("data", result)
        
        # Filter for invited members (unconfirmed memberships)
        invited_memberships = []
        if isinstance(memberships_data, list):
            for membership in memberships_data:
                if isinstance(membership, dict):
                    # Check if this is an unconfirmed membership (invited but not accepted)
                    unconfirmed = membership.get("unconfirmed", False)
                    if unconfirmed:
                        invited_memberships.append(membership)
        
        response = {
            "successful": True,
            "data": invited_memberships,
            "action": "get_invited_organization_members",
            "organization_id": idOrg,
            "total_invited_members": len(invited_memberships),
            "message": f"Successfully retrieved {len(invited_memberships)} invited member(s) for organization {idOrg}"
        }
        
        # Extract invited member information for easier access
        if invited_memberships:
            invited_member_ids = []
            invited_member_usernames = []
            invited_member_names = []
            invited_member_emails = []
            invited_member_initials = []
            membership_ids = []
            
            for membership in invited_memberships:
                if isinstance(membership, dict):
                    # Extract membership ID
                    if "id" in membership:
                        membership_ids.append(membership["id"])
                    
                    # Extract member information if available
                    if "member" in membership and isinstance(membership["member"], dict):
                        member_info = membership["member"]
                        if "id" in member_info:
                            invited_member_ids.append(member_info["id"])
                        if "username" in member_info:
                            invited_member_usernames.append(member_info["username"])
                        if "fullName" in member_info:
                            invited_member_names.append(member_info["fullName"])
                        if "email" in member_info:
                            invited_member_emails.append(member_info["email"])
                        if "initials" in member_info:
                            invited_member_initials.append(member_info["initials"])
            
            if membership_ids:
                response["membership_ids"] = membership_ids
            if invited_member_ids:
                response["invited_member_ids"] = invited_member_ids
            if invited_member_usernames:
                response["invited_member_usernames"] = invited_member_usernames
            if invited_member_names:
                response["invited_member_names"] = invited_member_names
            if invited_member_emails:
                response["invited_member_emails"] = invited_member_emails
            if invited_member_initials:
                response["invited_member_initials"] = invited_member_initials
        
        # Add helpful information
        if len(invited_memberships) == 0:
            response["note"] = "No pending invitations found for this organization"
        else:
            response["note"] = f"Found {len(invited_memberships)} pending invitation(s) - these members have not yet accepted their invitations"
        
        return response
        
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve invited organization members: {str(e)}",
            "action": "get_invited_organization_members",
            "organization_id": idOrg,
            "message": f"Failed to retrieve invited members for organization {idOrg}"
        }


@mcp.tool(
    "TRELLO_GET_ORGANIZATIONS_MEMBERS_INVITED_BY_ID_ORG_BY_FIELD",
    description="Get organization invited member field. Retrieves a specific `field` (e.g., fullname, username, email, status) for members with pending invitations to the trello organization specified by `idorg`.",
)
def TRELLO_GET_ORGANIZATIONS_MEMBERS_INVITED_BY_ID_ORG_BY_FIELD(
    idOrg: Annotated[str, "The ID or unique name of the organization to get invited member field for."],
    field: Annotated[str, "The specific field to retrieve for invited members (e.g., 'fullName', 'username', 'email', 'id', 'initials', 'avatarHash', 'bio', 'confirmed', 'memberType', 'url')."]
):
    """Get organization invited member field. Retrieves a specific `field` (e.g., fullname, username, email, status) for members with pending invitations to the trello organization specified by `idorg`."""
    err = _validate_required({"idOrg": idOrg, "field": field}, ["idOrg", "field"])
    if err:
        return err
    
    # Build the endpoint - use memberships endpoint to get invited members
    endpoint = f"/organizations/{idOrg}/memberships"
    
    # Build query parameters
    params = {
        "filter": "all",  # Get all memberships, we'll filter for invited ones
        "member": "true",  # Include member details
        "member_fields": field  # Get only the specific field requested
    }
    
    try:
        # Make the API request
        result = trello_request("GET", endpoint, params=params)
        
        if not isinstance(result, (list, dict)):
            return {
                "successful": False,
                "error": "Invalid memberships data received",
                "action": "get_invited_member_field",
                "organization_id": idOrg,
                "field": field,
                "message": f"Failed to retrieve invited member field '{field}' for organization {idOrg}"
            }
        
        # Handle both list and dict responses
        memberships_data = result if isinstance(result, list) else result.get("data", result)
        
        # Filter for invited members (unconfirmed memberships)
        invited_memberships = []
        if isinstance(memberships_data, list):
            for membership in memberships_data:
                if isinstance(membership, dict):
                    # Check if this is an unconfirmed membership (invited but not accepted)
                    unconfirmed = membership.get("unconfirmed", False)
                    if unconfirmed:
                        invited_memberships.append(membership)
        
        # Extract the specific field values from invited members
        field_values = []
        if invited_memberships:
            for membership in invited_memberships:
                if isinstance(membership, dict) and "member" in membership:
                    member_info = membership["member"]
                    if isinstance(member_info, dict) and field in member_info:
                        field_values.append(member_info[field])
        
        response = {
            "successful": True,
            "data": {
                "field": field,
                "values": field_values,
                "count": len(field_values)
            },
            "action": "get_invited_member_field",
            "organization_id": idOrg,
            "field": field,
            "total_invited_members": len(invited_memberships),
            "field_values": field_values,
            "message": f"Successfully retrieved field '{field}' for {len(field_values)} invited member(s) in organization {idOrg}"
        }
        
        # Add helpful information based on field type
        if field_values:
            if isinstance(field_values[0], str):
                response["field_type"] = "string"
                response["unique_values"] = list(set(field_values))
            elif isinstance(field_values[0], (int, float)):
                response["field_type"] = "number"
            elif isinstance(field_values[0], bool):
                response["field_type"] = "boolean"
            elif isinstance(field_values[0], list):
                response["field_type"] = "array"
            elif isinstance(field_values[0], dict):
                response["field_type"] = "object"
            else:
                response["field_type"] = "unknown"
        
        # Add helpful information
        if len(invited_memberships) == 0:
            response["note"] = "No pending invitations found for this organization"
        elif len(field_values) == 0:
            response["note"] = f"No invited members have the field '{field}' available"
        else:
            response["note"] = f"Retrieved '{field}' field for {len(field_values)} invited member(s)"
        
        return response
        
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to retrieve invited member field: {str(e)}",
            "action": "get_invited_member_field",
            "organization_id": idOrg,
            "field": field,
            "message": f"Failed to retrieve field '{field}' for invited members in organization {idOrg}"
        }


@mcp.tool(
    "TRELLO_GET_SEARCH_MEMBERS",
    description="Search for members. Searches trello members by name, username, or email, optionally scoped to a board or organization.",
)
def TRELLO_GET_SEARCH_MEMBERS(
    query: Annotated[str, "The search query to find members by name, username, or email."],
    idBoard: Annotated[Optional[str], "Optional board ID to limit search to members of that board."] = None,
    idOrganization: Annotated[Optional[str], "Optional organization ID to limit search to members of that organization."] = None,
    limit: Annotated[Optional[str], "Maximum number of members to return. Defaults to 8."] = "8",
    onlyOrgMembers: Annotated[Optional[str], "Whether to only return organization members. Defaults to false."] = None
):
    """Search for members. Searches trello members by name, username, or email, optionally scoped to a board or organization."""
    err = _validate_required({"query": query}, ["query"])
    if err:
        return err
    
    # Build the endpoint
    endpoint = "/search/members"
    
    # Build query parameters
    params = {
        "query": query
    }
    
    if idBoard is not None and idBoard.strip():
        params["idBoard"] = idBoard
    if idOrganization is not None and idOrganization.strip():
        params["idOrganization"] = idOrganization
    if limit is not None and limit.strip():
        params["limit"] = limit
    if onlyOrgMembers is not None and onlyOrgMembers.strip():
        params["onlyOrgMembers"] = onlyOrgMembers
    
    try:
        # Make the API request
        result = trello_request("GET", endpoint, params=params)
        
        if not isinstance(result, (list, dict)):
            return {
                "successful": False,
                "error": "Invalid search results received",
                "action": "search_members",
                "query": query,
                "message": f"Failed to search for members with query '{query}'"
            }
        
        # Handle both list and dict responses
        members_data = result if isinstance(result, list) else result.get("data", result)
        
        response = {
            "successful": True,
            "data": members_data,
            "action": "search_members",
            "query": query,
            "total_members_found": len(members_data) if isinstance(members_data, list) else 1,
            "message": f"Successfully found {len(members_data) if isinstance(members_data, list) else 1} member(s) for query '{query}'"
        }
        
        # Add search scope information
        if idBoard and idBoard.strip():
            response["search_scope"] = f"board:{idBoard}"
        if idOrganization and idOrganization.strip():
            response["search_scope"] = f"organization:{idOrganization}"
        if onlyOrgMembers and onlyOrgMembers.strip().lower() == "true":
            response["only_org_members"] = True
        
        # Extract member information for easier access
        if isinstance(members_data, list) and members_data:
            member_ids = []
            member_usernames = []
            member_names = []
            member_emails = []
            member_initials = []
            
            for member in members_data:
                if isinstance(member, dict):
                    if "id" in member:
                        member_ids.append(member["id"])
                    if "username" in member:
                        member_usernames.append(member["username"])
                    if "fullName" in member:
                        member_names.append(member["fullName"])
                    if "email" in member:
                        member_emails.append(member["email"])
                    if "initials" in member:
                        member_initials.append(member["initials"])
            
            if member_ids:
                response["member_ids"] = member_ids
            if member_usernames:
                response["member_usernames"] = member_usernames
            if member_names:
                response["member_names"] = member_names
            if member_emails:
                response["member_emails"] = member_emails
            if member_initials:
                response["member_initials"] = member_initials
        
        # Add helpful information
        if isinstance(members_data, list):
            if len(members_data) == 0:
                response["note"] = f"No members found matching query '{query}'"
            else:
                response["note"] = f"Found {len(members_data)} member(s) matching query '{query}'"
        
        return response
        
    except Exception as e:
        return {
            "successful": False,
            "error": f"Failed to search for members: {str(e)}",
            "action": "search_members",
            "query": query,
            "message": f"Failed to search for members with query '{query}'"
        }


@mcp.tool(
    "TRELLO_GET_SESSIONS_SOCKET",
    description="Get sessions socket. Note: Trello WebSocket functionality is not officially supported and has been deprecated. This tool provides information about alternatives for real-time updates.",
)
def TRELLO_GET_SESSIONS_SOCKET():
    """Get sessions socket. Note: Trello WebSocket functionality is not officially supported and has been deprecated. This tool provides information about alternatives for real-time updates."""
    
    # Return information about WebSocket deprecation and alternatives
    response = {
        "successful": False,
        "error": "Trello WebSocket functionality is not officially supported",
        "action": "get_sessions_socket",
        "message": "Trello WebSocket connections are not available through the official API",
        "deprecation_notice": "As of November 15, 2024, Trello deprecated WebSocket connections using query string authentication",
        "alternatives": {
            "webhooks": {
                "description": "Use Trello Webhooks for real-time updates",
                "endpoint": "https://api.trello.com/1/webhooks",
                "method": "HTTP POST callbacks when events occur",
                "documentation": "https://developer.atlassian.com/cloud/trello/guides/rest-api/webhooks/"
            },
            "polling": {
                "description": "Poll Trello API endpoints periodically",
                "method": "Make regular API calls to check for changes",
                "endpoints": [
                    "/boards/{id}/actions",
                    "/cards/{id}/actions", 
                    "/lists/{id}/actions"
                ]
            },
            "deltas": {
                "description": "Use organization deltas for incremental updates",
                "endpoint": "/organizations/{id}/deltas",
                "method": "Incremental fetching with update index"
            }
        },
        "recommended_approach": "Use Trello Webhooks for real-time updates",
        "webhook_setup": {
            "steps": [
                "1. Set up a publicly accessible URL endpoint",
                "2. Create a webhook using POST /1/webhooks",
                "3. Specify the model (board, card, etc.) and callback URL",
                "4. Handle incoming POST requests with event data"
            ],
            "example_endpoint": "https://your-domain.com/trello-webhook",
            "required_fields": ["idModel", "callbackURL", "description"]
        },
        "note": "For real-time updates, consider using Trello Webhooks instead of WebSocket connections"
    }
    
    return response


# -------------------- MAIN --------------------

if __name__ == "__main__":
    mcp.run()
