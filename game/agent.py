class Agent:
    def __init__(self):
        self.abilities = {
            "basic_repair": True,
            "enhanced_connections": False,
            "firewall": False,
            "data_redirect": False,
            "neural_override": False,
            "antivirus": False
        }
        self.energy_capacity = 100
        self.connection_cost_multiplier = 1.0
        self.movement_speed = 1.0
        
    def unlock_ability(self, ability_name):
        if ability_name in self.abilities:
            self.abilities[ability_name] = True
            
    def can_use_enhanced_connections(self):
        return self.abilities["enhanced_connections"]
    
    def can_use_antivirus(self):
        return self.abilities["antivirus"]
        
    def get_connection_cost(self, connection_type):
        costs = {
            "normal": 20,
            "enhanced": 40,
            "temporary": 15,
            "firewall": 30
        }
        base_cost = costs.get(connection_type, 20)
        return int(base_cost * self.connection_cost_multiplier)