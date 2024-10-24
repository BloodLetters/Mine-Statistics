import os

from supabase import create_client

class Database:
    def __init__(self):
        if os.getenv('SUPABASE_URL') != None:
            self.supabase_url = os.environ['SUPABASE_URL_BETA']
        else:
            self.supabase_url = os.environ['SUPABASE_URL']

        if os.getenv('SUPABASE_KEY_BETA') != None:
            self.supabase_key = os.environ['SUPABASE_KEY_BETA']
        else:
            self.supabase_key = os.environ['SUPABASE_KEY']
        
        self.client = create_client(self.supabase_url, self.supabase_key)

    def get_all_servers(self):
        return self.client.table('servers').select('*').execute()

    def get_server(self, server_ip, guild_id, server_port=None):
        query = self.client.table('servers').select('*').eq('server_ip', server_ip).eq("guild_id", guild_id)
        if server_port:
            query = query.eq('server_port', server_port)
        return query.execute()

    def get_Embed(self, guild_id, channel_id, message_id):
        return self.client.table('servers').select('*').eq('message_id', message_id).eq('channel_id', channel_id).eq("guild_id", guild_id).execute()

    def add_server(self, server_data):
        return self.client.table('servers').insert(server_data).execute()

    def fetch_message(self, message_id):
        return self.client.table('servers').select('*').eq('message_id', message_id).execute()

    def update_server(self, server_ip, data, server_port=None):
        query = self.client.table('servers').update(data).eq('server_ip', server_ip)
        if server_port:
            query = query.eq('server_port', server_port)
        return query.execute()

    def delete_server(self, server_ip, guild_id, server_port=None):
        query = self.client.table('servers').delete().eq('server_ip', server_ip).eq('guild_id', guild_id)
        if server_port:
            query = query.eq('server_port', server_port)
        return query.execute()
    
    def add_staff(self, user_id):
        return self.client.table('staff').insert({'user_id': user_id}).execute()

    def remove_staff(self, user_id):
        return self.client.table('staff').delete().eq('user_id', user_id).execute()

    def is_staff(self, user_id):
        result = self.client.table('staff').select('*').eq('user_id', user_id).execute()
        return len(result.data) >= 1

    def staff_list(self):
        result = self.client.table('staff').select('*').execute()
        return result.data

    def get_server_by_guild(self, guild_id):
        return self.client.table('servers').select('*').eq('guild_id', guild_id).execute()

    def add_server(self, server_data):
        return self.client.table('servers').insert(server_data).execute()

    def update_server(self, server_ip, data):
        return self.client.table('servers').update(data).eq('server_ip', server_ip).execute()

    def get_all_servers_chunk(self, limit, offset):
        return self.client.table('servers').select('*').range(offset, offset + limit - 1).execute()