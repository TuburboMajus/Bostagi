import subprocess
import tempfile
import shutil


FORBIDDEN_NAMES = ['ubuntu',"root"]

class Mailbox(object):
    """docstring for Mailbox"""
    def __init__(self, name=None, uid=None, gid=None, home=None, mail=None, address=None, alias=None, **kwargs):
        super(Mailbox, self).__init__()
        self.name = name if name is not None else alias
        self.uid = uid
        self.gid = gid
        self.home = home
        self.mail = mail
        self.alias = alias
        self.address = address

    def is_valid_mailbox(**kwargs):
        if kwargs.get('name') is None or kwargs['name'] in FORBIDDEN_NAMES:
            return False
        if kwargs.get('home') is None or not kwargs['home'].startswith('/home/'):
            return False
        if kwargs.get('mail') is None:
            return False
        return True

    def set_domain_name(self, domain_name):
        if domain_name is not None:
            self.address = f"{self.name if self.alias is None else self.alias}@{domain_name}"
        return self

    def generate(firstname=None, lastname=None):
        return Mailbox(alias=f"{firstname}.{lastname}")

    def __repr__(self):
        return f"Mailbox {self.name} (self.uid - self.gid) at {self.home} (address = {self.address})"


class Doveadm(object):

    """docstring for Doveadm"""
    def __init__(self, domain_name=None ,**kwargs):
        super(Doveadm, self).__init__()
        self.domain_name = domain_name
            
    def list_dovecot_users(self):
        """
        Lists all system users and checks if they are recognized by Dovecot.
        Uses `getent passwd` to list users and `doveadm user` to verify Dovecot validity.
        Returns a list of valid Dovecot mail users.
        """
        aliases = Doveadm.parse_aliases_file()

        try:
            # Construct the shell command
            cmd = r"""getent passwd | cut -d: -f1 | xargs -I {} sh -c 'echo {}; sudo doveadm user {}; echo "\n";'"""
            
            # Execute the command and capture output
            output = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.PIPE)
            
            # Parse output to extract valid users
            valid_users = []
            lines = output.split('\n')
            i = 0; j = 0
            current_user = {}
            while i < len(lines):
                line = lines[i]
                i += 1
                if len(line.strip()) == 0:
                    if current_user is not None and Mailbox.is_valid_mailbox(**current_user):
                        valid_users.append(Mailbox(**current_user,alias=aliases.get(current_user['name'],[None])[-1]).set_domain_name(self.domain_name))
                    current_user = {}; j = 0
                    continue
                if j == 0:
                    current_user['name'] = line.strip()
                elif j > 1:
                    try:
                        current_user[line.strip().replace('\t',' ').split(' ')[0].strip()] = line.strip().replace('\t',' ').split(' ')[1].strip()
                    except:
                        print(f"Exception at line {line}")
                        pass
                j += 1
            return valid_users
        
        except subprocess.CalledProcessError as e:
            print(f"Error executing command: {e.stderr}")
            return []
        except Exception as e:
            print(f"Unexpected error: {e}")
            return []

    def parse_aliases_file():
        """
        Reads /etc/aliases and returns a dictionary where:
        - Keys are usernames
        - Values are lists of aliases for that username
        
        Returns:
            dict: {username: [alias1, alias2, ...], ...}
            None: if file can't be read
        """
        aliases_file = '/etc/aliases'
        aliases_dict = {}
        
        try:
            with open(aliases_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    
                    # Skip comments and empty lines
                    if not line or line.startswith('#'):
                        continue
                    
                    # Split alias and username(s)
                    if ':' in line:
                        alias_part, users_part = line.split(':', 1)
                        alias = alias_part.strip()
                        usernames = [u.strip() for u in users_part.split(',')]
                        
                        # Add each username with its alias
                        for username in usernames:
                            if username:  # Skip empty usernames
                                if username in aliases_dict:
                                    aliases_dict[username].append(alias)
                                else:
                                    aliases_dict[username] = [alias]
        
        except FileNotFoundError:
            print(f"Error: {aliases_file} not found")
            return None
        except PermissionError:
            print(f"Error: Permission denied reading {aliases_file}")
            return None
        except Exception as e:
            print(f"Error reading {aliases_file}: {str(e)}")
            return None
        
        return aliases_dict

    def add_email_alias(alias, username):
        """
        Adds an email alias to /etc/aliases in the format: alias: username
        Then runs newaliases to update the alias database.
        
        Args:
            username (str): The target user who will receive emails
            alias (str): The email alias to add
        
        Returns:
            bool: True if successful, False otherwise
        """
        aliases = Doveadm.parse_aliases_file()
        if alias in aliases.get(username,[]):
            print(f"Alias {alias} already associated with user {username}")
            return True

        try:
            # Format the new alias entry
            new_entry = f"{alias}: {username}\n"
            
            # Create a temporary file
            with tempfile.NamedTemporaryFile(mode='w+') as tmp_file:
                # Copy existing aliases to temp file
                with open('/etc/aliases', 'r') as aliases_file:
                    tmp_file.write(aliases_file.read())
                
                # Add new entry
                tmp_file.write(new_entry)
                tmp_file.flush()
                
                # Replace the original file with the temp file
                shutil.copy(tmp_file.name, '/etc/aliases')
            
            # Update the alias database
            subprocess.check_call(['sudo', 'newaliases'])
            
            print(f"Alias '{alias}' for user '{username}' added successfully.")
            return True
            
        except PermissionError:
            print("Error: Permission denied. Try running with sudo.")
            return False
        except FileNotFoundError:
            print("Error: /etc/aliases file not found.")
            return False
        except subprocess.CalledProcessError:
            print("Error: Failed to run newaliases command.")
            return False
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return False

    def reset_mailbox_password(self, mailbox, password):
        """
        Adds a new Ubuntu user with the given username and password.
        Returns True if successful, False otherwise.
        """
        username = mailbox.name
        if '.' in mailbox.name:
            username = mailbox.name.replace('.','_')

        try:
            # Set the password using chpasswd
            subprocess.check_output(
                f"echo '{username}:{password}' | sudo chpasswd",
                shell=True,
                stderr=subprocess.STDOUT,
                text=True
            )

            print(f"Password for user '{username}' has been reset successfully.")
            return True

        except subprocess.CalledProcessError as e:
            print(f"Failed to reset password for user '{username}': {e.output}")
            return False

    def generate_new_mailbox(self, mailbox, password):
        """
        Adds a new Ubuntu user with the given username and password.
        Returns True if successful, False otherwise.
        """
        if '.' in mailbox.name:
            assert(Doveadm.add_email_alias(mailbox.name, mailbox.name.replace('.','_')))
        username = mailbox.name.replace('.','_')

        try:
            # Create the user with home directory and bash shell
            subprocess.check_output(
                ["sudo", "adduser", "--disabled-password", "--gecos", "", username],
                stderr=subprocess.STDOUT,
                text=True
            )

            # Set the password using chpasswd
            subprocess.check_output(
                f"echo '{username}:{password}' | sudo chpasswd",
                shell=True,
                stderr=subprocess.STDOUT,
                text=True
            )

            print(f"User '{username}' added successfully.")
            return True

        except subprocess.CalledProcessError as e:
            print(f"Failed to add user '{username}': {e.output}")
            return False

# Example usage
if __name__ == "__main__":
    Doveadm("genzbuilders.tn").generate_new_mailbox(Mailbox(alias="taief.hilali"),"aaaabbbb")
    dovecot_users = Doveadm("genzbuilders.tn").list_dovecot_users()
    print("Valid Dovecot users:")
    for user in dovecot_users:
        print(f"- {user}")
    Doveadm("genzbuilders").reset_mailbox_password(Mailbox(alias="taief.hilali"),"aaaacccc")



        
