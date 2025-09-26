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
    before: Annotated[str, "An action ID. Only return actions before this action."] = None,
    display: Annotated[str, "The format for the returned actions."] = None,
    entities: Annotated[str, "Whether to include entities in the response."] = None,
    fields: Annotated[str, "The fields to retrieve from the actions (e.g., id, type, date, data). Defaults to all."] = "all",
    filter: Annotated[str, "The types of actions to return (e.g., commentCard, updateCard). Defaults to commentCard and updateCard:idList."] = "commentCard,updateCard:idList",
    format: Annotated[str, "The format for the returned actions. Defaults to list."] = "list",
    id_models: Annotated[str, "The IDs of models to include in the response."] = None,
    limit: Annotated[str, "The maximum number of actions to return. Defaults to 50."] = "50",
    member: Annotated[str, "Whether to include member information."] = None,
    member_creator: Annotated[str, "Whether to include member creator information."] = None,
    member_creator_fields: Annotated[str, "The fields to retrieve from member creators. Defaults to avatarHash, fullName, initials and username."] = "avatarHash,fullName,initials,username",
    member_fields: Annotated[str, "The fields to retrieve from members. Defaults to avatarHash, fullName, initials and username."] = "avatarHash,fullName,initials,username",
    page: Annotated[str, "The page of results to return. Defaults to 0."] = "0",
    since: Annotated[str, "An action ID. Only return actions after this action."] = None
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


# -------------------- MAIN --------------------

if __name__ == "__main__":
    mcp.run()
