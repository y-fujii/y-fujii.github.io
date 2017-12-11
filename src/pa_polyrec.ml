(*
 * Camlp4 syntax extension for treating objects like records
 * by Yasuhiro Fujii <y-fujii at mimosa-pudica.net>, public domain
 *
 * compile: ocamlc -I +camlp4 -pp camlp4of dynlink.cma camlp4lib.cma pa_polyrec.ml
 *   usage: ocamlc -pp "camlp4o pa_polyrec.cmo" YOUR_SOURCE.ml
 *
 * example:
 *     let u = #{ x = 1; y = 2 }
 *     let v = #{ u with y = 3 }
 *)

open Camlp4.PreCast
open Syntax

EXTEND Gram
    GLOBAL: expr;

    expr: LEVEL "simple" [[
        "#"; "{"; fields = TRY[ e = field_list; "}" -> e ] ->
            let items = List.fold_left (fun acc (k, v) ->
                <:class_str_item<
                    $acc$
                    val $k$ = $v$
                    method $k$ = $lid:k$
                    method $"with_"^k$ = fun $lid:k^"'"$ -> {< $lid:k$ = $lid:k^"'"$ >}
                >>
            ) <:class_str_item<>> fields in
            <:expr< object $items$ end >>

        | "#"; "{"; orig = TRY[ e = expr LEVEL "."; "with" -> e ]; fields = field_list; "}" ->
            List.fold_left (fun acc (k, v) ->
                <:expr< $acc$ # $"with_"^k$ $v$ >>
            ) orig fields
    ]];

    field_list: [[
        e = field; ";"; es = SELF ->
            e :: es
        | e = field; ";" ->
            [e]
        | e = field ->
            [e]
    ]];

    field: [[
        k = a_LIDENT; "="; v = expr LEVEL "top" ->
            (k, v)
    ]];
END;
