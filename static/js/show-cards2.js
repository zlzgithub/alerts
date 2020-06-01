function show_content(n) {
    if (0 == n) {
        $("#section-cards-view").css('display', "none");
    }
    else {
        $("#section-cards-view").css('display', "block");
    }
}

function show_item(n) {
    if (0 == n) {
        $(".not_arrow_box").each(function () {
            $(this).parent().css('display', "none");
        });
    } else {
        $(".not_arrow_box").each(function () {
            $(this).parent().css('display', "block");
        });
    }
}

function show_all_cards(n) {
    if (n === 0) {
        show_content(0);
        show_item(1);
        show_content(1);

        // 初始显示全部
        $('[name="bsw-status"]').bootstrapSwitch({
            state: false,
            onText: "有问题",
            onColor: "warning",
            offText: "全部",
            offColor: "info",
            onSwitchChange: function (event, state) {
                if (state == true) {
                    show_item(0);
                } else {
                    show_item(1);
                }
            }
        });
    } else {
        show_content(0);
        show_item(0);
        show_content(1);

        // 初始显示有问题的
        $('[name="bsw-status"]').bootstrapSwitch({
            state: false,
            onText: "全部",
            onColor: "info",
            offText: "有问题",
            offColor: "warning",
            onSwitchChange: function (event, state) {
                if (state == false) {
                    show_item(0);
                } else {
                    show_item(1);
                }
            }
        })
    }
}
