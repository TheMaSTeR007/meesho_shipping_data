import subprocess


def get_git_repo_url(repo_directory):
    try:
        # Change to the repository directory
        result = subprocess.run(
            ['git', '-C', repo_directory, 'config', '--get', 'remote.origin.url'],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        # Decode and return the repository URL
        repo_url = result.stdout.decode('utf-8').strip()
        return repo_url
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr.decode('utf-8')}")
        return None


# Example usage
repo_directory = r'C:\Project Files Live (using Scrapy)\meesho\meesho_shipping_data'
git_repo_url = get_git_repo_url(repo_directory)

if git_repo_url:
    print(f"Git repository URL: {git_repo_url}")
