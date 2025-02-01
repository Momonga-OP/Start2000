import discord
from discord import app_commands
import os
import asyncio
import sys
import shutil
from typing import Optional
from discord.ext import commands

class Hunyuan3DCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.is_initialized = False
        
    async def run_subprocess(self, cmd, **kwargs):
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            **kwargs
        )
        stdout, stderr = await process.communicate()
        return process.returncode, stdout, stderr
        
    async def initialize_models(self):
        """Initialize the required models and dependencies"""
        if self.is_initialized:
            return True
            
        try:
            # Install huggingface-cli
            returncode, stdout, stderr = await self.run_subprocess(
                [sys.executable, "-m", "pip", "install", "huggingface_hub[cli]"]
            )
            
            if returncode != 0:
                print(f"Error installing huggingface-cli: {stderr.decode()}")
                return False
                
            # Create weights directory
            os.makedirs("weights", exist_ok=True)
            os.makedirs("weights/hunyuanDiT", exist_ok=True)
            
            # Download models asynchronously
            tasks = [
                self.run_subprocess(
                    ["huggingface-cli", "download", "tencent/Hunyuan3D-1", "--local-dir", "./weights"]
                ),
                self.run_subprocess(
                    ["huggingface-cli", "download", "Tencent-Hunyuan/HunyuanDiT-v1.1-Diffusers-Distilled", 
                     "--local-dir", "./weights/hunyuanDiT"]
                )
            ]
            
            results = await asyncio.gather(*tasks)
            
            for returncode, stdout, stderr in results:
                if returncode != 0:
                    print(f"Error downloading model: {stderr.decode()}")
                    return False
            
            self.is_initialized = True
            return True
            
        except Exception as e:
            print(f"Error during initialization: {str(e)}")
            return False
    
    @app_commands.command(name="setup_hunyuan", description="Initialize Hunyuan3D models and dependencies")
    @commands.has_permissions(administrator=True)
    async def setup_hunyuan(self, interaction: discord.Interaction):
        """Admin command to set up the Hunyuan3D environment"""
        await interaction.response.defer()
        
        await interaction.followup.send("Starting Hunyuan3D setup... This may take a while.")
        
        success = await self.initialize_models()
        
        if success:
            await interaction.followup.send("✅ Hunyuan3D setup completed successfully!")
        else:
            await interaction.followup.send("❌ Error setting up Hunyuan3D. Check the bot logs for details.")
    
    async def run_generation(self, command):
        """Run generation command asynchronously"""
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        return process.returncode, stdout, stderr
    
    @app_commands.command(name="text2mesh", description="Generate 3D mesh from text description")
    async def text2mesh(
        self,
        interaction: discord.Interaction,
        prompt: str,
        max_faces: Optional[int] = 90000,
        t2i_steps: Optional[int] = 25,
        gen_steps: Optional[int] = 50,
        seed: Optional[int] = 0
    ):
        if not self.is_initialized:
            await interaction.response.send_message(
                "⚠️ Hunyuan3D is not initialized. Please ask an admin to run `/setup_hunyuan` first."
            )
            return
            
        await interaction.response.defer()
        
        try:
            # Create output directory for this specific generation
            output_dir = f"./outputs/{interaction.user.id}_{interaction.id}"
            os.makedirs(output_dir, exist_ok=True)
            
            # Construct the command
            command = [
                "python3", "main.py",
                "--text_prompt", prompt,
                "--save_folder", output_dir,
                "--max_faces_num", str(max_faces),
                "--t2i_steps", str(t2i_steps),
                "--gen_steps", str(gen_steps),
                "--gen_seed", str(seed),
                "--do_texture_mapping",
                "--do_render"
            ]
            
            # Run the generation process asynchronously
            returncode, stdout, stderr = await self.run_generation(command)
            
            if returncode != 0:
                await interaction.followup.send(f"Error generating 3D mesh: {stderr.decode()}")
                return
                
            # Find the generated files
            mesh_file = None
            render_file = None
            for file in os.listdir(output_dir):
                if file.endswith(".obj"):
                    mesh_file = os.path.join(output_dir, file)
                elif file.endswith(".gif"):
                    render_file = os.path.join(output_dir, file)
            
            # Send the files
            files = []
            if mesh_file:
                files.append(discord.File(mesh_file))
            if render_file:
                files.append(discord.File(render_file))
                
            if files:
                await interaction.followup.send(
                    f"Generated 3D mesh from text: '{prompt}'",
                    files=files
                )
            else:
                await interaction.followup.send("No output files were generated.")
            
            # Clean up output directory
            shutil.rmtree(output_dir)
            
        except Exception as e:
            await interaction.followup.send(f"An error occurred: {str(e)}")
            
    @app_commands.command(name="image2mesh", description="Generate 3D mesh from an image")
    async def image2mesh(
        self,
        interaction: discord.Interaction,
        image: discord.Attachment,
        max_faces: Optional[int] = 90000,
        gen_steps: Optional[int] = 50,
        seed: Optional[int] = 0
    ):
        if not self.is_initialized:
            await interaction.response.send_message(
                "⚠️ Hunyuan3D is not initialized. Please ask an admin to run `/setup_hunyuan` first."
            )
            return
            
        await interaction.response.defer()
        
        try:
            # Download the image
            image_path = f"./temp_{interaction.id}.png"
            await image.save(image_path)
            
            # Create output directory
            output_dir = f"./outputs/{interaction.user.id}_{interaction.id}"
            os.makedirs(output_dir, exist_ok=True)
            
            # Construct the command
            command = [
                "python3", "main.py",
                "--image_prompt", image_path,
                "--save_folder", output_dir,
                "--max_faces_num", str(max_faces),
                "--gen_steps", str(gen_steps),
                "--gen_seed", str(seed),
                "--do_texture_mapping",
                "--do_render"
            ]
            
            # Run the generation process asynchronously
            returncode, stdout, stderr = await self.run_generation(command)
            
            # Clean up the temporary image
            if os.path.exists(image_path):
                os.remove(image_path)
            
            if returncode != 0:
                await interaction.followup.send(f"Error generating 3D mesh: {stderr.decode()}")
                return
                
            # Find the generated files
            mesh_file = None
            render_file = None
            for file in os.listdir(output_dir):
                if file.endswith(".obj"):
                    mesh_file = os.path.join(output_dir, file)
                elif file.endswith(".gif"):
                    render_file = os.path.join(output_dir, file)
            
            # Send the files
            files = []
            if mesh_file:
                files.append(discord.File(mesh_file))
            if render_file:
                files.append(discord.File(render_file))
                
            if files:
                await interaction.followup.send(
                    "Generated 3D mesh from the provided image",
                    files=files
                )
            else:
                await interaction.followup.send("No output files were generated.")
            
            # Clean up output directory
            shutil.rmtree(output_dir)
            
        except Exception as e:
            await interaction.followup.send(f"An error occurred: {str(e)}")

async def setup(bot: commands.Bot):
    await bot.add_cog(Hunyuan3DCommands(bot))
