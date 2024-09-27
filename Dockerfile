# Use an official lightweight Python image.
FROM python:3.12-slim

# Set the working directory in the container to /app
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your code into the container at /app
COPY . .

# Expose port (not necessary for Discord bots but included for completeness)
EXPOSE 8080

# Command to run when starting the container
CMD ["python", "bot.py"]
