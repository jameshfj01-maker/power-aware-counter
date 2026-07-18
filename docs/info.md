<!---

This file is used to generate your project datasheet. Please fill in the information below and delete any unused
sections.

You can also include images in this folder and reference them in the markdown. Each image must be less than
512 kb in size, and the combined size of all images must be less than 1 MB.
-->

## How it works

8비트 카운터를 클럭마다 1씩 증가시킨다. 일반 이진수로 출력하는 대신, 이진값을 그레이코드로 변환해서 출력한다 (binary_count ^ (binary_count >> 1)). 그레이코드는 값이 바뀔 때 항상 딱 1비트만 바뀌는 특성이 있어서, 여러 비트가 동시에 스위칭될 때 생기는 전력망 노이즈(di/dt)를 줄이는 효과가 있다. 비교를 위해 원래 이진 카운터 값도 uio 출력으로 함께 내보낸다.

## How to test

ui_in[0]을 1로 설정하면 카운터가 매 클럭마다 증가한다. uo_out에서 그레이코드 값을, uio_out에서 이진 카운터 값을 동시에 관찰하면서, 두 출력이 서로 다른 비트 전환 패턴을 보이는지 확인한다.

## External hardware

None.
