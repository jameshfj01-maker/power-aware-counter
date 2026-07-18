`default_nettype none

module tt_um_jameshfj01maker_power_aware_counter (
    input  wire [7:0] ui_in,
    output wire [7:0] uo_out,
    input  wire [7:0] uio_in,
    output wire [7:0] uio_out,
    output wire [7:0] uio_oe,
    input  wire       ena,
    input  wire       clk,
    input  wire       rst_n
);

  reg [7:0] binary_count;
  wire enable = ui_in[0];

  always @(posedge clk or negedge rst_n) begin
    if (!rst_n)
      binary_count <= 8'd0;
    else if (ena && enable)
      binary_count <= binary_count + 8'd1;
  end

  // 이진값을 그레이코드로 변환: 항상 딱 1비트만 바뀜
  wire [7:0] gray_count = binary_count ^ (binary_count >> 1);

  assign uo_out  = gray_count;    // 그레이코드 출력 (전력 노이즈 최소화)
  assign uio_out = binary_count;  // 비교용 이진 카운터 출력
  assign uio_oe  = 8'hFF;

  wire _unused = &{ui_in[7:1], uio_in, 1'b0};

endmodule
