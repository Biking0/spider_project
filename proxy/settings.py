# is_ok里的
from carrier.be import is_be_ok
from carrier.fr import is_fr_ok
from carrier.vy import is_vy_ok
from carrier.dg import is_dg_ok
from carrier.ww import is_ww_ok
from carrier.u2 import is_u2_ok
from carrier.f3 import is_f3_ok
from carrier.bx import is_bx_ok
from carrier.jq import is_jq_ok
from carrier.vj import is_vj_ok
from carrier.a7c import is_a7c_ok
from carrier.aq import is_aq_ok
from carrier.kn import is_kn_ok

# from carrier.tr import is_tr_ok
# from carrier.a5 import is_a5_ok
# from carrier.ad import is_ad_ok
# from carrier.v7 import is_v7_ok
# from carrier.ad import is_ad_ok
# from carrier.kc import is_kc_ok
# from carrier.hv import is_hv_ok
# from carrier._as import is_as_ok
# from carrier.dd import is_dd_ok
# from carrier.lx import is_lx_ok
# from carrier.ak import is_ak_ok
# from carrier.sl import is_sl_ok
# from carrier.mm import is_mm_ok
# from carrier.tw import is_tw_ok
# from carrier.ls import is_ls_ok

# is_did_ok专有的
from carrier.pc import is_pc_ok
from carrier.nk import is_nk_ok
from carrier.wn import is_wn_ok

CARRIER_FUNC = {
    'fr': is_fr_ok,
    'be': is_be_ok,
    'vy': is_vy_ok,
    'dg': is_dg_ok,
    'ww': is_ww_ok,
    'u2': is_u2_ok,
    'f3': is_f3_ok,
    '7c': is_a7c_ok,
    'bx': is_bx_ok,
    'jq': is_jq_ok,
    'vj': is_vj_ok,
    'aq': is_aq_ok,
    'kn': is_kn_ok
    # 'tr': is_tr_ok,
    # 'v7': is_v7_ok,
    # 'a5': is_a5_ok,
    # 'ad': is_ad_ok,
    # 'hv': is_hv_ok,
    # 'as': is_as_ok,
    # 'ls': is_ls_ok,
    # 'sl': is_sl_ok,
    # 'mm': is_mm_ok,
    # 'kc': is_kc_ok,
    # 'tw': is_tw_ok,
    # 'dd': is_dd_ok,
    # 'lx': is_lx_ok,
    # 'ak': is_ak_ok,
}

DID_FUNC = {
    'pc': is_pc_ok,
    'nk': is_nk_ok,
    'wn': is_wn_ok,
}
