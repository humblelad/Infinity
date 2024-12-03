import subprocess
import random
import colorsys

# Function to get human-defined users dynamically
def get_human_defined_users():
    try:
        result = subprocess.run(
            "awk -F: '($3 >= 1000 && $3 < 65534) && $1 != \"nobody\" {print $1}' /etc/passwd",
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        usernames = result.stdout.strip().split('\n')
        usernames.append("others")
        return usernames
    except subprocess.CalledProcessError as e:
        print(f"Error while retrieving users: {e.stderr}")
        return []

# Function to generate distinct colors
def generate_distinct_colors(num_colors):
    colors = []
    for i in range(num_colors):
        hue = 0.15 + (i / num_colors) * 0.8
        saturation = 0.8 + random.random() * 0.2  
        value = 0.8 + random.random() * 0.2       
        
        rgb = colorsys.hsv_to_rgb(hue, saturation, value)
        hex_color = '#{:02x}{:02x}{:02x}'.format(
            int(rgb[0] * 255),
            int(rgb[1] * 255),
            int(rgb[2] * 255)
        )
        colors.append(hex_color)
    return colors
# Function to write colors to a file
def write_colors_file(usernames, output_path):
    colors = generate_distinct_colors(len(usernames))
    with open(output_path, 'w') as f:
        f.write(f"root:red\n")
        for username, color in zip(usernames, colors):
            f.write(f"{username}:{color}")
            if username != usernames[-1]:
                f.write('\n')

# Main Program
if __name__ == "__main__":
    usernames = get_human_defined_users()
    if usernames:
        output_path = './sysadmin/templates/colors.txt'
        write_colors_file(usernames, output_path)
    else:
        print("No human-defined users found.")
