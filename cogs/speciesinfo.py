# Command: /speciesinfo <species_name / natdex_num>

import discord
from discord.ext import commands
from discord import app_commands
import json

try:
    with open("data/species_info.json", "r", encoding="utf-8") as f:
        pokemon_data = json.load(f)
except FileNotFoundError:
    print("ERROR: species_info.json file not found!")
    pokemon_data = []
except json.JSONDecodeError:
    print("ERROR: Invalid JSON format in species_info.json!")
    pokemon_data = []


def get_available_pages(species):
    """Determine which pages have content for this species"""
    pages = [1]  # Page 1 (basic info) is always available
    
    # Check if page 2 (evolutions/forms) has content
    has_evolutions = "evolutions" in species and species["evolutions"]
    has_form_changes = "formChanges" in species and species["formChanges"]
    if has_evolutions or has_form_changes:
        pages.append(2)
    
    # Check if page 3 (level-up moves) has content
    if "levelUpMoves" in species and species["levelUpMoves"]:
        pages.append(3)
    
    # Check if page 4 (egg moves) has content
    if "eggMoves" in species and species["eggMoves"]:
        pages.append(4)
    
    # Check if page 5 (teachable moves) has content
    if "teachableLearnset" in species and species["teachableLearnset"]:
        pages.append(5)
    
    return pages


def format_ev_yield(species):
    """Format EV yield information into a readable string"""
    ev_stats = []
    ev_fields = ["evYield_HP", "evYield_Attack", "evYield_Defense", 
                 "evYield_SpAttack", "evYield_SpDefense", "evYield_Speed"]
    
    stat_names = {
        "evYield_HP": "HP",
        "evYield_Attack": "Attack",
        "evYield_Defense": "Defense",
        "evYield_SpAttack": "Sp. Attack",
        "evYield_SpDefense": "Sp. Defense",
        "evYield_Speed": "Speed"
    }
    
    for field in ev_fields:
        if field in species and species[field] > 0:
            ev_stats.append(f"{stat_names[field]}: {species[field]}")
    
    if ev_stats:
        return ", ".join(ev_stats)
    return "None"


def build_embed(species, page_num, available_pages):
    """Builds the embed for the given page of species info."""
    # Map the virtual page number to the actual content type
    page_type = available_pages[page_num - 1]
    
    if page_type == 1:  # Basic info
        embed = discord.Embed(
            title=f"{species['speciesName']} (#{species['natDexNum']})",
            description=f"{species['monCategory']} Pokémon",
            color=discord.Color.red()
        )
        embed.add_field(name="Types", value=", ".join(species.get("types", [])), inline=False)
        embed.add_field(
            name="Stats",
            value=(
                f"HP: {species['stats']['hp']}\n"
                f"Attack: {species['stats']['attack']}\n"
                f"Defense: {species['stats']['defense']}\n"
                f"Sp. Attack: {species['stats']['spAttack']}\n"
                f"Sp. Defense: {species['stats']['spDefense']}\n"
                f"Speed: {species['stats']['speed']}"
            ),
            inline=False
        )
        embed.add_field(name="Abilities", value=", ".join(species.get("Abilities", [])), inline=False)
        embed.add_field(name="Hidden Ability", value=species.get("Hidden Ability", "None"), inline=False)
        embed.add_field(name="Catch Rate", value=species.get("catchRate", "N/A"), inline=True)
        embed.add_field(name="Exp Yield", value=species.get("expYield", "N/A"), inline=True)
        embed.add_field(name="EV Yield", value=format_ev_yield(species), inline=False)
        embed.add_field(name="Height", value=species.get('height', 'N/A'), inline=True)
        embed.add_field(name="Weight", value=species.get('weight', 'N/A'), inline=True)
        embed.add_field(name="Egg Cycles", value=species.get('eggCycles', 'N/A'), inline=True)
        return embed

    elif page_type == 2:  # Evolutions and form changes
        embed = discord.Embed(
            title=f"{species['speciesName']} - Evolutions & Forms",
            color=discord.Color.green()
        )
        
        # Add evolutions if present
        has_evolutions = "evolutions" in species and species["evolutions"]
        if has_evolutions:
            evo_text = ""
            for evo in species["evolutions"]:
                evo_text += f"**{evo.get('targetSpecies', 'Unknown')}**\n"
                evo_text += f"Method: {evo.get('method', 'Unknown')}\n"
                if "Item" in evo:
                    evo_text += f"Item: {evo['Item']}\n"
                evo_text += "\n"
            embed.add_field(name="Evolutions", value=evo_text, inline=False)
        else:
            embed.add_field(name="Evolutions", value="None", inline=False)
        
        # Add form changes if present
        has_form_changes = "formChanges" in species and species["formChanges"]
        if has_form_changes:
            form_text = ""
            for form in species["formChanges"]:
                form_text += f"**{form.get('targetSpecies', 'Unknown')}**\n"
                form_text += f"Method: {form.get('method', 'Unknown')}\n"
                if "Item" in form:
                    form_text += f"Item: {form['Item']}\n"
                form_text += "\n"
            embed.add_field(name="Form Changes", value=form_text, inline=False)
        else:
            embed.add_field(name="Form Changes", value="None", inline=False)
            
        return embed

    elif page_type == 3:  # Level-up moves
        moves = [f"Lv {m['level']}: {m['move']}" for m in species.get("levelUpMoves", [])]
        text = "\n".join(moves) if moves else "None"
        embed = discord.Embed(
            title=f"{species['speciesName']} - Level-Up Moves",
            description=text,
            color=discord.Color.blue()
        )
        return embed

    elif page_type == 4:  # Egg moves
        text = "\n".join(species.get("eggMoves", [])) or "None"
        embed = discord.Embed(
            title=f"{species['speciesName']} - Egg Moves",
            description=text,
            color=discord.Color.orange()
        )
        return embed

    elif page_type == 5:  # Teachable moves
        text = "\n".join(species.get("teachableLearnset", [])) or "None"
        embed = discord.Embed(
            title=f"{species['speciesName']} - Teachable Moves",
            description=text,
            color=discord.Color.purple()
        )
        return embed


class SpeciesView(discord.ui.View):
    def __init__(self, species, available_pages):
        super().__init__(timeout=6000)  # ~1hr timeout
        self.species = species
        self.available_pages = available_pages
        self.page_num = 1  # Current page index (1-based)
        self.max_pages = len(available_pages)

    @discord.ui.button(label="◀ Prev", style=discord.ButtonStyle.secondary)
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page_num = self.max_pages if self.page_num == 1 else self.page_num - 1
        await interaction.response.edit_message(
            embed=build_embed(self.species, self.page_num, self.available_pages), 
            view=self
        )

    @discord.ui.button(label="Next ▶", style=discord.ButtonStyle.secondary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page_num = 1 if self.page_num == self.max_pages else self.page_num + 1
        await interaction.response.edit_message(
            embed=build_embed(self.species, self.page_num, self.available_pages), 
            view=self
        )


class SpeciesInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def _get_species_autocomplete(self):
        """Helper function to get all species names for autocomplete"""
        return [species["speciesName"] for species in pokemon_data]

    async def species_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str
    ) -> list[app_commands.Choice[str]]:
        species_names = self._get_species_autocomplete()
        return [
            app_commands.Choice(name=name, value=name)
            for name in species_names
            if current.lower() in name.lower()
        ][:25]  # Discord limits to 25 choices

    @app_commands.command(
        name="speciesinfo",
        description="Get information about a Pokémon species"
    )
    @app_commands.describe(query="The Pokémon name or National Dex number")
    @app_commands.autocomplete(query=species_autocomplete)
    async def speciesinfo(self, interaction: discord.Interaction, query: str):
        try:
            query = query.strip().lower()
            result = None

            for species in pokemon_data:
                # Handle both numbers and names
                if query.isdigit():
                    if int(query) == int(species["natDexNum"]):
                        result = species
                        break
                else:
                    if query == species["speciesName"].lower():
                        result = species
                        break

            if result:
                available_pages = get_available_pages(result)
                embed = build_embed(result, 1, available_pages)
                view = SpeciesView(result, available_pages)
                await interaction.response.send_message(embed=embed, view=view)
            else:
                await interaction.response.send_message(f"No Pokémon found for '{query}'", ephemeral=True)

        except ValueError:
            await interaction.response.send_message("Please enter a valid number for National Dex search.", ephemeral=True)
        except KeyError as e:
            await interaction.response.send_message(f"Data format error: Missing key {e}", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"An unexpected error occurred: {e}", ephemeral=True)
            print(f"Error in speciesinfo command: {e}")


async def setup(bot):
    await bot.add_cog(SpeciesInfo(bot))
