# this file creates the completion function and adds it to the completion system
function _gitty () {
    cmds=`gitty zsh | tail -n1`
    a=("${(@s/ /)cmds}")
    compadd ${a}
}
compdef _gitty gitty
