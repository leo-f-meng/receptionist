from dataclasses import dataclass
from datetime import datetime, timedelta

from dateutil import parser
from livekit.agents import AgentTask, RunContext, function_tool


@dataclass
class VisitorCheckinState:
    visitor_name: str | None = None
    host_name: str | None = None
    has_appointment: bool | None = None
    appointment_time: str | None = None
    host_status: str | None = None


INS = """
You are assisting with visitor check-in at a building reception desk.

Your goal is to collect the following information:

1. visitor name
2. host name
3. whether the visitor has an appointment
4. appointment time (if there is one)

Rules:
• Ask only for missing information.
• Do not ask for information already known.
• Be polite and concise like a receptionist.

When all information is collected:
• Inform the visitor appropriately.

"""


@function_tool()
async def start_visitor_checkin(
    context: RunContext,
    visitor_name: str | None = None,
    host_name: str | None = None,
    has_appointment: bool | None = None,
    appointment_time: str | None = None,
) -> None:
    """
    Start the visitor check-in workflow.

    Use this when a visitor says they are here to see someone,
    have a meeting, or need to check in.

     Args:
        visitor_name: Pre-collected visitor name (optional)
        host_name: Pre-collected host name (optional)
        has_appointment: Pre-collected appointment status (optional)
        appointment_time: Pre-collected appointment time (optional)
    """

    await VisitorCheckinTask(
        context.session._chat_ctx,
        visitor_name=visitor_name,
        host_name=host_name,
        has_appointment=has_appointment,
        appointment_time=appointment_time,
    )


class VisitorCheckinTask(AgentTask[VisitorCheckinState]):

    def __init__(
        self,
        chat_ctx,
        visitor_name: str | None = None,
        host_name: str | None = None,
        has_appointment: bool | None = None,
        appointment_time: str | None = None,
    ):
        super().__init__(
            instructions=INS,
            chat_ctx=chat_ctx,
        )
        self.state = VisitorCheckinState(
            visitor_name=visitor_name,
            host_name=host_name,
            has_appointment=has_appointment,
            appointment_time=appointment_time,
        )

    # Task entry point
    async def on_enter(self):
        if not self.state.visitor_name:
            await self.session.generate_reply(
                instructions="Welcome the visitor and ask for their name."
            )
            return

        if not self.state.host_name:
            await self.session.generate_reply(
                instructions=f"Nice to meet {self.state.visitor_name}. Ask who they are visiting."
            )
            return

        if self.state.has_appointment is None:
            await self.session.generate_reply(
                instructions="Ask if they have an appointment."
            )
            return

        if self.state.has_appointment and not self.state.appointment_time:
            await self.session.generate_reply(
                instructions="Ask what time the appointment is."
            )
            return

        await self.check_host_status()

    @function_tool()
    async def record_checkin_info(
        self,
        context: RunContext,
        visitor_name: str | None = None,
        host_name: str | None = None,
        has_appointment: bool | None = None,
        appointment_time: str | None = None,
    ):
        """
        Record visitor check-in information.

        Extract any information the visitor provides.

        Args:
            visitor_name: name of the visitor
            host_name: name of the host they are visiting
            has_appointment: whether the visitor has an appointment
            appointment_time: time of the appointment if known
        """

        if visitor_name:
            self.state.visitor_name = visitor_name

        if host_name:
            self.state.host_name = host_name

        if has_appointment is not None:
            self.state.has_appointment = has_appointment

        if appointment_time:
            self.state.appointment_time = appointment_time

        await self.on_enter()

    @function_tool()
    async def unrelated_query(self, context: RunContext):
        """When user asks any unrelated questions or requests any other services not in your job description,
        run tool calling to generate the answer"""
        await self.session.generate_reply(instructions="Sure — Let me see.")
        self.complete(self.state)

    async def handle_host_status(self):
        visitor = self.state.visitor_name
        host = self.state.host_name
        status = self.state.host_status

        # check the time now and compare with appointment time if available, and adjust the message accordingly
        if self.state.has_appointment and self.state.appointment_time:
            time_now = datetime.now()
            appointment_time = parser.parse(
                self.state.appointment_time, default=time_now
            )

            # Visitor arrives more than 1 hour before appointment
            if time_now < appointment_time - timedelta(hours=1):
                await self.session.say(
                    text=f"""
                    Thanks {visitor}. But you're a bit early for your appointment with {host} at {self.state.appointment_time}.
                    I'll let {host} know you've arrived, but you might want to wait a bit before heading up.
                    """
                )
            # Visitor arrives more than 1 hour after appointment
            elif time_now > appointment_time + timedelta(hours=1):
                await self.session.say(
                    text=f"""
                    Thanks {visitor}. But you're a bit late for your appointment with {host} at {self.state.appointment_time}.
                    I'll let {host} know you've arrived, but you might want to give them a call.
                    """
                )
            # Visitor arrives within 1 hour of appointment. Check host status as normal.
            else:
                if status == "available":
                    await self.session.say(
                        text=f"""
                        Thanks {visitor}.
                        {host} is available.
                        I'll let them know you've arrived.
                        Please take a seat.
                    """
                    )

                elif status == "busy":
                    await self.session.say(
                        text=f"""
                            Thanks {visitor}.
                            {host} is currently in a meeting.
                            I'll let them know you're here.
                            Please take a seat.
                        """
                    )

                elif status == "away":
                    await self.session.say(
                        text=f"""
                            Thanks {visitor}.
                            It looks like {host} isn't at their desk right now.
                            I'll try to reach them for you.
                        """
                    )

                else:
                    await self.session.say(
                        text=f"""
                            Thanks {visitor}.
                            I'm having trouble confirming {host}'s availability.
                            Let me try to contact them. Please take a seat and wait for a moment. I'll let them know you've arrived.
                    """
                        # TODO: Implement host contact logic here, e.g. send a message or page to the host
                    )

        # No appointment time provided, so just check host status as normal
        else:
            await self.session.say(
                text=f"""
                Thanks {visitor}.
                I'll check if {host} is available to see you.
                """
            )
            if status == "available":
                await self.session.say(
                    text=f"""
                    Thanks {visitor}.
                    {host} is available.
                    I'll let them know you've arrived.
                    Please take a seat.
                """
                )

            elif status == "busy":
                await self.session.say(
                    text=f"""
                        Thanks {visitor}.
                        {host} is currently in a meeting.
                        I'll let them know you're here.
                        Please take a seat.
                    """
                )

            elif status == "away":
                await self.session.say(
                    text=f"""
                        Thanks {visitor}.
                        It looks like {host} isn't at their desk right now.
                        I'll try to reach them for you.
                    """
                )

            else:
                await self.session.say(
                    text=f"""
                        Thanks {visitor}.
                        I'm having trouble confirming {host}'s availability.
                        Let me try to contact them. Please take a seat and wait for a moment. I'll let them know you've arrived.
                """
                    # TODO: Implement host contact logic here, e.g. send a message or page to the host
                )

        self.complete(self.state)

    async def check_host_status(self):

        role_availability_mock_up = {
            "Adam": "away",
            "Dave": "available",
            "John": "busy",
            "Emily": None,
        }

        if self.state.host_name is not None:
            for host, status in role_availability_mock_up.items():
                if host.lower() == self.state.host_name.lower():
                    self.state.host_status = status
                    break

        await self.handle_host_status()
