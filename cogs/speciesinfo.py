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


def build_embed(species, page: int):
    """Builds the embed for the given page of species info."""
    if page == 1:
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
        embed.set_footer(text=f"Height: {species.get('height', 'N/A')} | Weight: {species.get('weight', 'N/A')}")
        return embed

    elif page == 2:  # Level-up moves
        moves = [f"Lv {m['level']}: {m['move']}" for m in species.get("levelUpMoves", [])]
        text = "\n".join(moves) if moves else "None"
        return discord.Embed(
            title=f"{species['speciesName']} - Level-Up Moves",
            description=text,
            color=discord.Color.blue()
        )

    elif page == 3:  # Egg moves
        text = "\n".join(species.get("eggMoves", [])) or "None"
        return discord.Embed(
            title=f"{species['speciesName']} - Egg Moves",
            description=text,
            color=discord.Color.orange()
        )

    elif page == 4:  # Teachable moves
        text = "\n".join(species.get("teachableLearnset", [])) or "None"
        return discord.Embed(
            title=f"{species['speciesName']} - Teachable Moves",
            description=text,
            color=discord.Color.purple()
        )


class SpeciesView(discord.ui.View):
    def __init__(self, species):
        super().__init__(timeout=6000)  # ~1hr timeout
        self.species = species
        self.page = 1

    @discord.ui.button(label="◀ Prev", style=discord.ButtonStyle.secondary)
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page = 4 if self.page == 1 else self.page - 1
        await interaction.response.edit_message(embed=build_embed(self.species, self.page), view=self)

    @discord.ui.button(label="Next ▶", style=discord.ButtonStyle.secondary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page = 1 if self.page == 4 else self.page + 1
        await interaction.response.edit_message(embed=build_embed(self.species, self.page), view=self)


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
                embed = build_embed(result, 1)
                view = SpeciesView(result)
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
