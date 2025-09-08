import discord
from discord.ext import commands
import json

with open("species_info.json", "r", encoding="utf-8") as f:
    pokemon_data = json.load(f)


def build_embed(species, page: int):
    """Builds the embed based on which page we're on."""
    if page == 1:
        embed = discord.Embed(
            title=f"{species['speciesName']} (#{species['natDexNum']})",
            description=f"{species['monCategory']} Pokémon",
            color=discord.Color.green()
        )
        embed.add_field(name="Types", value=", ".join(species["types"]), inline=False)
        embed.add_field(
            name="Stats",
            value=(
                f"HP: {species['stats']['hp']} | Atk: {species['stats']['attack']} | Def: {species['stats']['defense']}\n"
                f"SpA: {species['stats']['spAttack']} | SpD: {species['stats']['spDefense']} | Spe: {species['stats']['speed']}"
            ),
            inline=False
        )
        embed.add_field(name="Abilities", value=", ".join(species["Abilities"]), inline=True)
        embed.add_field(name="Hidden Ability", value=species["Hidden Ability"], inline=True)
        embed.add_field(name="Catch Rate", value=species["catchRate"], inline=True)
        embed.add_field(name="Exp Yield", value=species["expYield"], inline=True)
        embed.set_footer(text=f"Height: {species['height']} | Weight: {species['weight']}")
        return embed

    elif page == 2:  # Level-up moves
        moves = [f"Lv {m['level']}: {m['move']}" for m in species["levelUpMoves"]]
        text = "\n".join(moves) or "None"
        return discord.Embed(
            title=f"{species['speciesName']} - Level-Up Moves",
            description=text,
            color=discord.Color.blue()
        )

    elif page == 3:  # Egg moves
        text = "\n".join(species["eggMoves"]) or "None"
        return discord.Embed(
            title=f"{species['speciesName']} - Egg Moves",
            description=text,
            color=discord.Color.orange()
        )

    elif page == 4:  # Teachable moves
        text = "\n".join(species["teachableLearnset"]) or "None"
        return discord.Embed(
            title=f"{species['speciesName']} - Teachable Moves",
            description=text,
            color=discord.Color.purple()
        )


class SpeciesView(discord.ui.View):
    def __init__(self, species):
        super().__init__(timeout=60)  # 1 min timeout
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

    @commands.command()
    async def speciesinfo(self, ctx, *, query: str):
        query = query.strip().lower()

        result = None
        for species in pokemon_data:
            species_id = str(int(species["natDexNum"]))  # normalize natDexNum
            species_name = species["speciesName"].lower()

            if query == species_id or query == species_name:
                result = species
                break

        if result:
            embed = build_embed(result, 1)
            view = SpeciesView(result)
            await ctx.send(embed=embed, view=view)
        else:
            await ctx.send(f"No Pokémon found for '{query}'")

async def setup(bot):
    await bot.add_cog(SpeciesInfo(bot))
