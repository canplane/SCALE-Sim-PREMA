import trace_gen_wrapper as tg

from misc import set_style, set_color


def run_slot(arch, task, scheduler):
    print("")
    print(f"Network : \t{set_style(set_color(task.name, key=task.color), key='BOLD')}")
    print(f"Token   : \t{task.token:{'' if type(task.token) == int else '.3f'}} (Priority: {task.priority})")
    print("----------------------------------------------------")
    
    while task.current_layer_idx < len(task.layers):
        scheduler.recent_switched_epoch_time = scheduler.epoch_time

        layer = task.layers[task.current_layer_idx]

        print(f"{'Continuing' if task.last_executed_layer_idx == task.current_layer_idx else 'Commencing'} run for {set_style(set_color(layer.name, key=task.color), key='BOLD')} ({task.current_layer_idx + 1}/{len(task.layers)})")
        task.last_executed_layer_idx = task.current_layer_idx

        avg_bw_log, detail_log, sram_cycles, util = tg.gen_all_traces(arch, layer, scheduler)
        max_bw_log = tg.gen_max_bw_numbers(trace_paths=layer.trace_paths)
        
        with open(task.log_paths['avg_bw'], 'a') as f:
            f.write(f"{layer.name},\t{arch.sram_sz['ifmap']},\t{arch.sram_sz['filt']},\t{arch.sram_sz['ofmap']},\t" + avg_bw_log + '\n')
        with open(task.log_paths['max_bw'], 'a') as f:
            f.write(f"{layer.name},\t{arch.sram_sz['ifmap']},\t{arch.sram_sz['filt']},\t{arch.sram_sz['ofmap']},\t" + max_bw_log + '\n')
        with open(task.log_paths['detail'], 'a') as f:
            f.write(f"{layer.name},\t" + detail_log + '\n')
        with open(task.log_paths['cycles'], 'a') as f:
            f.write(f"{layer.name},\t{sram_cycles},\t{util}," + '\n')

        ####
        task.current_layer_idx += 1
        if task.current_layer_idx < len(task.layers):
            scheduler.refresh(a_layer_end=True)
            print("")
        ####
    #
#