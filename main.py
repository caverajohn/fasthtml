# import os
from datetime import datetime
import pytz
from supabase import create_client
from dotenv import load_dotenv

from fasthtml.common import *

# Load environment variables
load_dotenv()

MAX_NAME_CHAR = 15
MAX_MESSAGE_CHAT = 30
TIMESTAMP_FMT = "%Y-%m-%d %I:%M:%S CET"
# Initialize supabase client
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

app, rt = fast_app(
    hdrs=(Link(rel="icon", type="assets/x-icon", href="/assets/favicon.png"),),
)


def get_cet_time():
    cet_tz = pytz.timezone("America/Sao_Paulo")
    return datetime.now(cet_tz)


def add_message(name, message):
    timestamp = get_cet_time().strftime(TIMESTAMP_FMT)
    supabase.table("MyGuestbook").insert(
        {"name": name, "message": message, "timestamp": timestamp}
    ).execute()


def get_messages():
    # Sort by 'id' in descending order to get the latest entries first
    response = (
        supabase.table("MyGuestbook").select("*").order("id", desc=True).execute()
    )
    return response.data


def render_message(entry):
    return (
        Article(
            Header(f"Name: {entry["name"]}"),
            P(entry["message"]),
            Footer(Small(Em(f"Posted: {entry['timestamp']}"))),
        ),
    )


def render_message_list():
    messages = get_messages()

    return Div(*[render_message(entry) for entry in messages], id="message-list")


def render_content():
    form = (
        (
            Form(
                Fieldset(
                    Input(
                        type="text",
                        name="name",
                        placeholder="Your name",
                        required=true,
                        maxlength=MAX_NAME_CHAR,
                    ),
                    Input(
                        type="text",
                        name="message",
                        placeholder="Message",
                        required=true,
                        maxlength=MAX_MESSAGE_CHAT,
                    ),
                    Button("Submit", type="submit"),
                    role="group",
                ),
                method="post",
                hx_post="/submit-message",  # Send a POST request to the /submit-message endpoint
                hx_target="#message-list",  # Only swap the message list
                hx_swap="outerHTML",  # Replace the entire content of the target element with the ...
                hx_on_after_request="this.reset()",  # Reset the form after submission
            ),
        ),
    )
    return Div(
        P(Em("Write something nice 🤗")),
        form,
        Div(
            "Made with ❤️ by  ",
            A("John Cavera!!", href="https://www.deadcode.com.br", target="_blank"),
        ),
        Hr(),
        render_message_list(),
    )


@rt("/change")
def get():
    return Titled(
        "Change!!", P("Nice to be here {change}", A("Go back to homr", href="/"))
    )


@rt("/")
def get():
    return Titled("My Guest Book!!", render_content())


@rt("/submit-message", methods=["POST"])
def post(name: str, message: str):
    add_message(name, message)
    return render_message_list()


serve()
