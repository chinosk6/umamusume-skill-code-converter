from . import vars as vs
import typing as t


class UmaSkillCodeParser:
    def __init__(self, lang="cn"):
        if not hasattr(vs, lang):
            raise ValueError(f"language {lang} not found")
        self.lang = lang
        self.symbols_int, self.symbols_none, self._attr = self.setlang(lang)

    def setlang(self, lang: str, _isc=False):
        if not hasattr(vs, lang):
            raise ValueError(f"language {lang} not found")
        _attr = getattr(vs, lang)
        ret = [_attr.symbols_int, _attr.symbols_none]
        if _isc:
            self.symbols_int, self.symbols_none = ret
            self._attr = _attr
        ret.append(_attr)
        return ret

    def int_parser(self, code: str, natu: str, utype: int, value: str, default=1, types: t.Optional[t.List] = None,
                   trans_symbol=None):
        """
        :param code: 代码
        :param natu: 自然语言
        :param utype: 比较类型
        :param value: 比较值
        :param default: 默认值
        :param types: 用于dict
        :param trans_symbol: -
        """
        _types = vs.TypesOfUma.Compare
        utype_trans = self._attr.trans_type_compare[utype] if trans_symbol is None else trans_symbol[utype]
        ret = ""
        if types is not None:
            if utype == _types.NotEqualTo:
                if len(types) == 2:
                    _value = int(value)
                    ret = f"{types[0 if _value == 1 else 1]}"
                else:
                    ret = f"{utype_trans}{types[int(value)]}"
            else:
                ret = f"{types[int(value)]}{utype_trans}"

        else:
            if utype == _types.EqualsTo:
                if str(value) == "1":
                    ret = natu
                if str(value) == "0":
                    ret = f"没有{natu}"

            elif utype == _types.NotEqualTo:
                if str(value) == "0":
                    ret = natu

        ret = f"{natu}{utype_trans}{value}" if ret == "" else ret
        if "rate" in code or "_per" in code:
            ret = f"{ret}%"
        return ret

    def none_parser(self, code: str, natu: str, utype: int, value: str):
        def types_retter(data):
            for _uts, _ret in data:
                if utype in _uts:
                    return _ret

        _types = vs.TypesOfUma.Compare
        if code == "change_order_onetime":  # 排名更改
            return types_retter([[[_types.LessThan, _types.LessOrEquas], f"超过{int(value) + 1}人"],
                                 [[_types.GreaterOrEquals, _types.GreaterThan], f"名次下降{int(value) + 1}以上"],
                                 [[_types.EqualsTo], f"名次{'下降' if int(value) > 0 else '提升'}{value}以上"]])

        elif code == "bashin_diff_behind":
            return types_retter([[[_types.LessThan, _types.LessOrEquas], f"距离后方{value}马身外"],
                                 [[_types.GreaterOrEquals, _types.GreaterThan], f"距离后方{value}马身内"],
                                 [[_types.EqualsTo], f"距离后方{value}马身"]])

        elif code in ["order"]:
            return f"{natu}{self._attr.trans_type_symbol[utype]}{value}"

        elif code == "always":
            if utype == _types.EqualsTo:
                if value == "1":
                    return "无特殊条件"

        elif code == "random_lot":
            if utype == _types.EqualsTo:
                return f"{natu}%{value}"

        elif code == "track_id":
            if utype == _types.EqualsTo:
                return f"{self._attr.tracks[value]}{natu}"

        elif code == "distance_rate_after_random":
            return natu.format(value)

        return f"{code}{self._attr.trans_type_symbol[utype]}{value}"

    @staticmethod
    def spliter(skill_code: str):
        utypes = vs.TypesOfUma
        ret = []
        for code in skill_code.split("@"):
            code = code.strip()
            if ">=" in code:
                usymble, value = code.split(">=")
                utype = utypes.Compare.GreaterOrEquals
            elif "<=" in code:
                usymble, value = code.split("<=")
                utype = utypes.Compare.LessOrEquas
            elif "==" in code:
                usymble, value = code.split("==")
                utype = utypes.Compare.EqualsTo
            elif ">" in code:
                usymble, value = code.split(">")
                utype = utypes.Compare.GreaterThan
            elif "<" in code:
                usymble, value = code.split("<")
                utype = utypes.Compare.LessThan
            elif "!=" in code:
                usymble, value = code.split("!=")
                utype = utypes.Compare.NotEqualTo
            else:
                raise ValueError(f"{code} 中没有找到标识符")

            ret.append([usymble.strip(), utype, value.strip()])
        return ret

    def _final_checker(self, ret: str):
        def _resplit(_data: str):
            _ret = ""
            _split = _data.split(",")
            for i in _split:
                _i = i.strip()
                if _i != "":
                    _ret += f", {_i}"
            return _ret[1:].strip()

        _types = vs.TypesOfUma.Compare

        if self.symbols_int["is_finalcorner"][0] in ret and \
                self.symbols_int["corner"]["types"][0] in ret:
            ret = ret.replace(self.symbols_int["is_finalcorner"][0], "")  # 最终直线
            ret = ret.replace(self.symbols_int["corner"]["types"][0],
                              self._attr.sp["final_straight"])

        _spring = f"({self.symbols_int['season']['types'][1]}) {self._attr.or_} " \
                  f"({self.symbols_int['season']['types'][1]})"
        if _spring in ret:
            ret = ret.replace(_spring, self.symbols_int['season']['types'][1])

        return _resplit(ret)

    def get_nature_lang(self, code: str):
        if code is None or code.strip() == "":
            return "-"
        codes = code.split("&")
        retstr = ""

        for scode in codes:
            try:
                _retstr = ""
                _scodes = self.spliter(scode)
                for usymble, utype, value in _scodes:
                    if usymble in self.symbols_int:
                        _data_type = type(self.symbols_int[usymble])
                        if _data_type == str:
                            _d = self.int_parser(usymble, self.symbols_int[usymble], utype, value, 1)
                        elif _data_type == dict:
                            if "trans_type_symbol" in self.symbols_int[usymble]:
                                _trans_symbol = self.symbols_int[usymble]["trans_type_symbol"]
                            else:
                                _trans_symbol = None

                            _d = self.int_parser(usymble, self.symbols_int[usymble]["name"], utype, value,
                                                 self.symbols_int[usymble]["default"],
                                                 types=self.symbols_int[usymble]["types"], trans_symbol=_trans_symbol)
                        else:
                            if len(self.symbols_int[usymble]) == 3:
                                _trans_symbol = self.symbols_int[usymble][2]
                            else:
                                _trans_symbol = None
                            _d = self.int_parser(usymble, self.symbols_int[usymble][0], utype, value,
                                                 self.symbols_int[usymble][1], trans_symbol=_trans_symbol)
                        _retstr += f", {_d}"

                    elif usymble in self.symbols_none:
                        _retstr += f", {self.none_parser(usymble, self.symbols_none[usymble], utype, value)}"
                    else:
                        print(usymble)
                        _retstr += f", {usymble}{self._attr.trans_type_symbol[utype]}{value}"
                    _retstr += f" ,{self._attr.or_}"
                retstr += f"{_retstr[:-2 - len(self._attr.or_)].strip()}"
            except BaseException as e:
                retstr += f", {scode}"
                print(scode, e)
        ret = retstr[1:].strip()
        if f",{self._attr.or_}," in ret:
            ret = f"({ret.replace(f',{self._attr.or_},', f') {self._attr.or_} (')})"\
                .replace(" )", ")").replace("( ", "(")
        return self._final_checker(ret)
