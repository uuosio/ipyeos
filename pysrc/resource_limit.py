from .database import (Database, ResourceLimitsConfigObjectIndex,
                       ResourceLimitsObjectIndex,
                       ResourceLimitsStateObjectIndex,
                       ResourceUsageObjectIndex)
from .types import Name


class ResourceLimit(object):

    def __init__(self, db: Database):
        self.db = db
        self.resource_limits_config_object_index = ResourceLimitsConfigObjectIndex(db)
        self.resource_limits_state_object_index = ResourceLimitsStateObjectIndex(db)
        self.resource_limits_object_index = ResourceLimitsObjectIndex(db)
        self.resource_usage_object_index = ResourceUsageObjectIndex(db)

    def get_resource_limits_state_object(self):
        return self.resource_limits_state_object_index.get()

    def get_resource_limits_config_object(self):
        return self.resource_limits_config_object_index.get()

    def get_resource_limits_object(self, owner: Name, pending: bool=False):
        return self.resource_limits_object_index.find_by_owner(pending, owner)

    def get_resource_usage_object(self, owner: Name):
        return self.resource_usage_object_index.find_by_owner(owner)

# uint64_t resource_limits_manager::get_total_cpu_weight() const {
#    const auto& state = _db.get<resource_limits_state_object>();
#    return state.total_cpu_weight;
# }
    def get_total_cpu_weight(self) -> int:
        state = self.get_resource_limits_state_object()
        return state.total_cpu_weight
    
# uint64_t resource_limits_manager::get_total_net_weight() const {
#    const auto& state = _db.get<resource_limits_state_object>();
#    return state.total_net_weight;
# }
    def get_total_net_weight(self) -> int:
        state = self.get_resource_limits_state_object()
        return state.total_net_weight

# uint64_t resource_limits_manager::get_virtual_block_cpu_limit() const {
#    const auto& state = _db.get<resource_limits_state_object>();
#    return state.virtual_cpu_limit;
# }
    def get_virtual_block_cpu_limit(self) -> int:
        state = self.get_resource_limits_state_object()
        return state.virtual_cpu_limit

# uint64_t resource_limits_manager::get_virtual_block_net_limit() const {
#    const auto& state = _db.get<resource_limits_state_object>();
#    return state.virtual_net_limit;
# }
    def get_virtual_block_net_limit(self) -> int:
        state = self.get_resource_limits_state_object()
        return state.virtual_net_limit

# uint64_t resource_limits_manager::get_block_cpu_limit() const {
#    const auto& state = _db.get<resource_limits_state_object>();
#    const auto& config = _db.get<resource_limits_config_object>();
#    return config.cpu_limit_parameters.max - state.pending_cpu_usage;
# }
    def get_block_cpu_limit(self) -> int:
        state = self.get_resource_limits_state_object()
        config = self.get_resource_limits_config_object()
        return config.cpu_limit_parameters.max - state.pending_cpu_usage

# uint64_t resource_limits_manager::get_block_net_limit() const {
#    const auto& state = _db.get<resource_limits_state_object>();
#    const auto& config = _db.get<resource_limits_config_object>();
#    return config.net_limit_parameters.max - state.pending_net_usage;
# }
    def get_block_net_limit(self) -> int:
        state = self.get_resource_limits_state_object()
        config = self.get_resource_limits_config_object()
        return config.net_limit_parameters.max - state.pending_net_usage

# std::pair<int64_t, bool> resource_limits_manager::get_account_cpu_limit( const account_name& name, uint32_t greylist_limit ) const {
#    auto [arl, greylisted] = get_account_cpu_limit_ex(name, greylist_limit);
#    return {arl.available, greylisted};
# }

# bool resource_limits_manager::is_unlimited_cpu( const account_name& account ) const {
#    const auto* buo = _db.find<resource_limits_object,by_owner>( boost::make_tuple(false, account) );
#    if (buo) {
#       return buo->cpu_weight == -1;
#    }
#    return false;
# }
    def is_unlimited_cpu(self, account: str) -> bool:
        buo = self.get_resource_limits_object(account)
        if buo:
            return buo.cpu_weight == -1
        return False

# void resource_limits_manager::get_account_limits( const account_name& account, int64_t& ram_bytes, int64_t& net_weight, int64_t& cpu_weight ) const {
#    const auto* pending_buo = _db.find<resource_limits_object,by_owner>( boost::make_tuple(true, account) );
#    if (pending_buo) {
#       ram_bytes  = pending_buo->ram_bytes;
#       net_weight = pending_buo->net_weight;
#       cpu_weight = pending_buo->cpu_weight;
#    } else {
#       const auto& buo = _db.get<resource_limits_object,by_owner>( boost::make_tuple( false, account ) );
#       ram_bytes  = buo.ram_bytes;
#       net_weight = buo.net_weight;
#       cpu_weight = buo.cpu_weight;
#    }
# }
    def get_account_limits(self, account: str) -> (int, int, int):
        pending_buo = self.get_resource_limits_object(account)
        if pending_buo:
            ram_bytes = pending_buo.ram_bytes
            net_weight = pending_buo.net_weight
            cpu_weight = pending_buo.cpu_weight
        else:
            buo = self.get_resource_limits_object(account, pending=True)
            ram_bytes = buo.ram_bytes
            net_weight = buo.net_weight
            cpu_weight = buo.cpu_weight
        return (ram_bytes, net_weight, cpu_weight)

# int64_t resource_limits_manager::get_account_ram_usage( const account_name& name )const {
#    return _db.get<resource_usage_object,by_owner>( name ).ram_usage;
# }
    def get_account_ram_usage(self, name: str) -> int:
        obj = self.get_resource_usage_object(name)
        if not obj:
            raise Exception("unknown account %s" % name)
        return obj.ram_usage
