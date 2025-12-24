#pragma once

#include <cstdint>
#include <vector>

typedef int (*HookFunType)(void *func, void *replace, void **backup);

typedef int (*UnhookFunType)(void *func);

typedef void (*NativeOnModuleLoaded)(const char *name, void *handle);

typedef struct {
    uint32_t version;
    HookFunType hook_func;
    UnhookFunType unhook_func;
} NativeAPIEntries;

[[maybe_unused]] typedef NativeOnModuleLoaded (*NativeInit)(const NativeAPIEntries *entries);

typedef struct t_l2c_ccb tL2C_CCB;
typedef struct t_l2c_lcb tL2C_LCB;

uintptr_t loadHookOffset(const char* package_name);
uintptr_t getModuleBase(const char *module_name);
uintptr_t loadL2cuProcessCfgReqOffset();
uintptr_t loadL2cCsmConfigOffset();
uintptr_t loadL2cuSendPeerInfoReqOffset();
bool findAndHookFunction(const char *library_path);

#define SDP_MAX_ATTR_LEN 400

typedef struct t_sdp_di_record {
  uint16_t vendor;
  uint16_t vendor_id_source;
  uint16_t product;
  uint16_t version;
  bool primary_record;
  char client_executable_url[SDP_MAX_ATTR_LEN];
  char service_description[SDP_MAX_ATTR_LEN];
  char documentation_url[SDP_MAX_ATTR_LEN];
} tSDP_DI_RECORD;

typedef enum : uint8_t {
  BTA_SUCCESS = 0, /* Successful operation. */
  BTA_FAILURE = 1, /* Generic failure. */
  BTA_PENDING = 2, /* API cannot be completed right now */
  BTA_BUSY = 3,
  BTA_NO_RESOURCES = 4,
  BTA_WRONG_MODE = 5,
} tBTA_STATUS;