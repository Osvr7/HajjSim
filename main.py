import json

from hajj_agents import AgentFactory, PilgrimAgent, StaticProfile


def build_profile(item):
    return StaticProfile(
        pilgrim_id=item["pilgrim_id"],
        age=item["age"],
        nationality=item["nationality"],
        group_id=item["group_id"],
        mobility=item.get("mobility", item.get("base_mobility", 1.0)),
        health_status=item.get("health_status", "stable"),
        chronic_conditions=tuple(item.get("chronic_conditions", [])),
        language=item.get("language", "Arabic"),
        risk_tolerance=item.get("risk_tolerance", 0.5),
    )


def load_agents_from_file(filename):
    """Reads the JSON file and creates a dictionary of PilgrimAgent objects."""
    with open(filename, "r", encoding="utf-8") as file:
        data = json.load(file)

    agents_dictionary = {}

    for item in data:
        profile = build_profile(item)
        agent = PilgrimAgent(
            static_profile=profile,
            initial_node=item["initial_node"],
            target_node=item.get("target_node", "Arafat"),
        )

        social_memory = item.get("social_memory", {})
        agent.memory.social.leader_id = social_memory.get("leader_id")
        agent.memory.social.known_companions = social_memory.get("known_companions", [])
        agent.memory.social.help_contacts = social_memory.get("help_contacts", [])
        agent.memory.social.group_last_seen_node = social_memory.get("group_last_seen_node")

        long_term_memory = item.get("long_term_memory", {})
        agent.memory.long_term.known_routes = long_term_memory.get("known_routes", {})
        agent.memory.long_term.known_hazards = long_term_memory.get("known_hazards", {})
        agent.memory.long_term.learned_preferences = long_term_memory.get(
            "learned_preferences",
            {},
        )
        agent.memory.long_term.ritual_progress = long_term_memory.get("ritual_progress", [])

        agents_dictionary[agent.profile.pilgrim_id] = agent

    return agents_dictionary


def display_agent_info(agent):
    """Prints a formatted summary of the pilgrim's four-layer anatomy."""
    snapshot = agent.get_snapshot()
    profile = snapshot["profile"]
    state = snapshot["state"]
    memory = snapshot["memory"]

    print("\n" + "=" * 52)
    print(f"PILGRIM AGENT: {profile['pilgrim_id']}")
    print("=" * 52)
    print("1. STATIC PROFILE")
    print(
        f"Age: {profile['age']} | Nationality: {profile['nationality']} | "
        f"Group: {profile['group_id']}"
    )
    print(
        f"Mobility: {profile['mobility']} | Health: {profile['health_status']} | "
        f"Language: {profile['language']}"
    )
    print(
        f"Risk Tolerance: {profile['risk_tolerance']} | "
        f"Conditions: {', '.join(profile['chronic_conditions']) or 'None'}"
    )
    print("-" * 52)
    print("2. DYNAMIC STATE")
    print(
        f"Current Node: {state['current_node']} | Target: {state['target_node']} | "
        f"Last Action: {state['last_action']}"
    )
    print(
        f"Fatigue: {state['fatigue']:.1f} | Stress: {state['stress']:.1f} | "
        f"Hydration: {state['hydration']:.1f}"
    )
    print(
        f"With Group: {state['is_with_group']} | Panic: {state['is_panicking']} | "
        f"Tick: {state['simulation_tick']}"
    )
    print("-" * 52)
    print("3. MEMORY")
    print(f"Short-Term Nodes : {memory['short_term']['recent_nodes']}")
    print(f"Short-Term Events: {memory['short_term']['recent_events']}")
    print(f"Long-Term Hazards: {memory['long_term']['known_hazards']}")
    print(f"Social Links     : {memory['social']['known_companions']}")
    print(f"Group Last Seen  : {memory['social']['group_last_seen_node']}")
    print("=" * 52 + "\n")


def main():
    print("Loading HajjSim Environment...")
    agents = load_agents_from_file("pilgrims.json")
    print(f"Successfully loaded {len(agents)} agents.\n")
    factory = AgentFactory(seed=42)

    while True:
        print("Available Pilgrim IDs:", ", ".join(agents.keys()))
        user_input = input(
            "Enter a Pilgrim ID, 'step', 'generate <count>', or 'exit': "
        ).strip()

        if user_input.lower() == "exit":
            print("Exiting HajjSim...")
            break

        if user_input.lower() == "step":
            environment_data = {
                "density": 5.5,
                "temperature": 39.0,
                "group_location": "Mina_Camp_4",
                "alternate_node": "Shade_Corridor",
                "panic_node": "Emergency_Point",
            }
            for agent in agents.values():
                agent.step(environment_data)
            print("Simulation advanced by one tick.\n")
            continue

        if user_input.lower().startswith("generate"):
            parts = user_input.split()
            count = int(parts[1]) if len(parts) > 1 else 10
            generated_agents = factory.generate_agents(count=count, start_index=len(agents) + 1)
            agents.update(generated_agents)
            print(f"Generated {count} synthetic pilgrims.\n")
            continue

        if user_input in agents:
            display_agent_info(agents[user_input])
        else:
            print("Invalid ID. Please try again.\n")


if __name__ == "__main__":
    main()
