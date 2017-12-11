(*
 * camlp4 macro for treating objects like records
 * by y.fujii <y-fujii at mimosa-pudica.net>, public domain
 *
 * compile: ocamlc -I +camlp4 -c -pp "camlp4r pa_extend.cmo q_MLast.cmo" polyrec.ml
 *)

open Pcaml;

(* yank & paste from camlp4/etc/pa_o.ml *)
let stream_peek_nth n strm =
  loop n (Stream.npeek n strm) where rec loop n =
    fun
    [ [] -> None
    | [x] -> if n == 1 then Some x else None
    | [_ :: l] -> loop (n - 1) l ]
in

(* yank & paste from camlp4/etc/pa_o.ml *)
let test_label_eq =
  Grammar.Entry.of_parser gram "test_label_eq"
    (test 1 where rec test lev strm =
       match stream_peek_nth lev strm with
       [ Some (("UIDENT", _) | ("LIDENT", _) | ("", ".")) ->
           test (lev + 1) strm
       | Some ("", "=") -> ()
       | _ -> raise Stream.Failure ])
in


EXTEND
    GLOBAL: expr;

    expr: LEVEL "simple"
    [[
        "{"; "#"; test_label_eq; fields = rec_field_list; "}" ->
            MLast.ExObj _loc None fields
            (* <:expr< object $list:fields$ end >> *)

        | "{"; "#"; org = expr; "with"; fields = with_field_list; "}" ->
            List.fold_left (fun acc (k, v) ->
                <:expr< $acc$ # $"with_"^k$ $v$ >>
            ) org fields
    ]];

    rec_field_list:
    [[
        e = rec_field; ";"; es = rec_field_list ->
            [e :: es]
        | e = rec_field; ";" ->
            [e]
        | e = rec_field ->
            [e]
    ]];

    rec_field:
    [[
        k = LIDENT; "="; v = expr ->
            <:class_str_item<
                declare
                    value $k$ = $v$;
                    method $k$ = $lid:k$;
                    method $"with_"^k$ = fun $lid:k^"'"$ ->
                        {< $k$ = $lid:k^"'"$ >};
                end
            >>
    ]];

    with_field_list:
    [[
        e = with_field; ";"; es = with_field_list ->
            [e :: es]
        | e = with_field; ";" ->
            [e]
        | e = with_field ->
            [e]
    ]];

    with_field:
    [[
        k = LIDENT; "="; v = expr ->
            (k, v)
    ]];
END;
