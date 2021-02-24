#include <eosio/eosio.hpp>
extern "C" {
    __attribute__((eosio_wasm_import))
    void set_kv_parameters_packed( const char* data, uint32_t datalen );
}

using namespace eosio;
struct kv_parameters {
  /**
  * The maximum key size
  * @brief The maximum key size
  */
  uint32_t max_key_size;

  /**
  * The maximum value size
  * @brief The maximum value size
  */
  uint32_t max_value_size;

  /**
   * The maximum number of iterators
  * @brief The maximum number of iterators
   */
  uint32_t max_iterators;

  EOSLIB_SERIALIZE( kv_parameters,
                    (max_key_size)
                    (max_value_size)(max_iterators)
  )
};
inline void set_kv_parameters(const kv_parameters& params) {
  // set_kv_parameters_packed expects version, max_key_size,
  // max_value_size, and max_iterators,
  // while kv_parameters only contains max_key_size, max_value_size,
  // and max_iterators. That's why we place uint32_t in front
  // of kv_parameters in buf
  char buf[sizeof(uint32_t) + sizeof(kv_parameters)];
  eosio::datastream<char *> ds( buf, sizeof(buf) );
  ds << uint32_t(0);  // fill in version
  ds << params;
  ::set_kv_parameters_packed( buf, ds.tellp() );
}
extern "C" void apply(uint64_t receiver, uint64_t first_receiver, uint64_t action) {
    kv_parameters params;
    params.max_key_size = 64;
    params.max_value_size = 256;
    params.max_iterators = 100;
    set_kv_parameters(params);
    return;
}
