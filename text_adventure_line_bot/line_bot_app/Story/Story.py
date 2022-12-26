from transitions.extensions import GraphMachine 
from .functions import call_func_with_str,get_options,print_state_text
from transitions.extensions.states import add_state_features, Timeout

# add timeout feature to machine to implement QTE action
@add_state_features(Timeout)
class GraphMachineWithTimeout(GraphMachine):
    pass

class Story(object):
    # endings
    non_twist_endings=['true_ending','good_ending','neutral_ending','bad_ending']
    twist_endings=['pandemic_ending']
    all_endings=non_twist_endings+twist_endings
    
    # state with timeout(left hook, fight back) will require player to act within 5 seconds
    states=['story_begin','abandoned_city','more_info','stray_dog',
    'get_bitten','dog_eating','homeless_man','choose_homeless_man_topic',
    'dialog_about_homeless_man','city_dialog_with_homeless_man','sister_dialog_with_homeless_man',
    'mutant_town',{'name':'left_hook','timeout':5,'on_timeout':'too_slow'},'saved_by_dog',{'name':'fight_back','timeout':5,'on_timeout':'too_slow'},'dialog_with_angry_mutant',
    'magician','choose_magician_topic','jewlery_dialog','sister_dialog_with_magician',
    'mutant_town_dialog_with_magician','shelter2','scientist','choose_scientist_topic',
    'experiment_dialog','world_dialog','sister_dialog_with_scientist','your_sister',
    'choose_sister_topic','father_dialog','follow_dialog','choose_new_dest','stray_dog_has_left',
    'has_checked_angry_mutant'
    ]+all_endings

    def __init__(self):
        self.machine=GraphMachineWithTimeout(model=self,states=Story.states,initial='story_begin',ignore_invalid_triggers=True,show_conditions=True,show_state_attributes=True)
        self.has_been_bitten=False 
        self.has_got_jewlery=False
        self.asked_sister_to_follow=False
        self.has_fed_dog=False
        self.angry_mutant_plot_is_triggered=False
        # acted too slow in angry mutant plot
        self.user_acted_too_slow=False

        # SECTION stray_dog in abandoned_city
        
        # don't trigger plot of stray dog twice in a game
        self.machine.add_transition('check_stray_dog','abandoned_city','stray_dog',unless='has_triggered_dog_plot')
        self.machine.add_transition('check_stray_dog','abandoned_city','stray_dog_has_left',conditions='has_triggered_dog_plot')
        self.machine.add_transition('confirm','stray_dog_has_left','abandoned_city')

        self.machine.add_transition('leave_stray_dog','stray_dog','abandoned_city')
        self.machine.add_transition('pet_dog','stray_dog','get_bitten') 
        self.machine.add_transition('feed_dog','stray_dog','dog_eating') 
        self.machine.add_transition('confirm',['dog_eating','get_bitten'],'abandoned_city')

        # SECTION homeless_man in abandoned_city
        self.machine.add_transition('check_homeless_man','abandoned_city','homeless_man')
        self.machine.add_transition('leave_homeless_man','homeless_man','abandoned_city')
        self.machine.add_transition('talk','homeless_man','choose_homeless_man_topic',unless=['trigger_true_ending','trigger_good_ending'])

        self.machine.add_transition('ask_about_the_city','choose_homeless_man_topic','city_dialog_with_homeless_man')
        self.machine.add_transition('ask_about_your_sister','choose_homeless_man_topic','sister_dialog_with_homeless_man')
        self.machine.add_transition('ask_about_homeless_man','choose_homeless_man_topic','dialog_about_homeless_man')

        self.machine.add_transition('end_homeless_man_dialog',
        ['sister_dialog_with_homeless_man',
        'city_dialog_with_homeless_man',
        'dialog_about_homeless_man'
        ],'homeless_man') # end dialog with homeless man

        # SECTION go to/ leave abandoned_city
        self.machine.add_transition('go_to_abandoned_city','story_begin','abandoned_city')
        self.machine.add_transition('leave','abandoned_city','choose_new_dest')        

        # SECTION angry mutant states
        # prevent trigger plot twice in a game
        self.machine.add_transition('check_angry_mutant','mutant_town','left_hook',unless='has_triggered_angry_mutant_plot')
        self.machine.add_transition('check_angry_mutant','mutant_town','has_checked_angry_mutant',conditions='has_triggered_angry_mutant_plot')
        self.machine.add_transition('confirm','has_checked_angry_mutant','mutant_town')

        # SECTION left_hook state
        self.machine.add_transition('dodge_to_right','left_hook','bad_ending',unless='twist_bad_ending')
        # print options after make transition automatically
        self.machine.add_transition('too_slow','left_hook','bad_ending',
        unless='twist_bad_ending',after='after_too_slow_transition')

        self.machine.add_transition('run_away','left_hook','bad_ending',unless='twist_bad_ending')
        self.machine.add_transition('dodge_to_left','left_hook','fight_back')

        # twist 2, if you've fed dog in abandoned city, you will be saved by it when triggering bad ending
        self.machine.add_transition('dodge_to_right','left_hook','saved_by_dog',conditions='twist_bad_ending')
        # print options after make transition automatically
        self.machine.add_transition('too_slow','left_hook','saved_by_dog',
        conditions='twist_bad_ending',after='after_too_slow_transition')

        self.machine.add_transition('run_away','left_hook','saved_by_dog',conditions='twist_bad_ending')

        self.machine.add_transition('talk_with_angry_mutant','saved_by_dog','dialog_with_angry_mutant')

        # SECTION fight back
        self.machine.add_transition('run_away','fight_back','saved_by_dog',conditions='twist_bad_ending')
        self.machine.add_transition('too_slow','fight_back','saved_by_dog',
        conditions='twist_bad_ending',after='after_too_slow_transition')

        self.machine.add_transition('punch','fight_back','dialog_with_angry_mutant')

        self.machine.add_transition('run_away','fight_back','bad_ending')
        self.machine.add_transition('too_slow','fight_back','bad_ending',
        unless='twist_bad_ending',after='after_too_slow_transition')

        self.machine.add_transition('end_dialog','dialog_with_angry_mutant','mutant_town')
        
        # SECTION magician states
        self.machine.add_transition('check_magician','mutant_town','magician')
        self.machine.add_transition('leave_magician','magician','mutant_town')
        self.machine.add_transition('talk','magician','choose_magician_topic')
        self.machine.add_transition('ask_about_his_jewlery','choose_magician_topic','jewlery_dialog')
        self.machine.add_transition('ask_about_mutant_town','choose_magician_topic','mutant_town_dialog_with_magician')
        self.machine.add_transition('ask_about_your_sister','choose_magician_topic','sister_dialog_with_magician')
        self.machine.add_transition('end_dialog',
        ['jewlery_dialog','sister_dialog_with_magician','mutant_town_dialog_with_magician'],
        'magician')

        # SECTION mutant town transitions
        self.machine.add_transition('go_to_mutant_town','story_begin','mutant_town')
        self.machine.add_transition('leave','mutant_town','choose_new_dest')

        # SECTION scientist states
        self.machine.add_transition('check_scientist','shelter2','scientist')
        self.machine.add_transition('leave_scientist','scientist','shelter2')
        self.machine.add_transition('talk','scientist','choose_scientist_topic')
        self.machine.add_transition('ask_about_her_experiment','choose_scientist_topic','experiment_dialog')
        self.machine.add_transition('ask_her_about_your_sister','choose_scientist_topic','sister_dialog_with_scientist')
        self.machine.add_transition('ask_her_about_the_world','choose_scientist_topic','world_dialog')
        self.machine.add_transition('end_dialog',['experiment_dialog','sister_dialog_with_scientist','world_dialog'],'scientist')

        # SECTION your sister states
        self.machine.add_transition('check_your_sister','shelter2','your_sister')
        self.machine.add_transition('leave_your_sister','your_sister','shelter2')
        self.machine.add_transition('talk','your_sister','choose_sister_topic')

        self.machine.add_transition('ask_her_to_follow_you','choose_sister_topic','follow_dialog') 
        self.machine.add_transition('talk_about_your_father','choose_sister_topic','father_dialog')

        self.machine.add_transition('end_dialog',['father_dialog','follow_dialog'],'your_sister')
        # ending states

        self.machine.add_transition('go_home','choose_sister_topic','neutral_ending')

        # twist 1, you will have pandemic ending if you've pet dog in abandoned city, and had neutral/good ending
        self.machine.add_transition('restart',['good_ending','neutral_ending'],'pandemic_ending',conditions='trigger_twist_ending')
        self.machine.add_transition('restart',['good_ending','neutral_ending'],'story_begin',unless='trigger_twist_ending') # allow every game to restart after new game
        
        self.machine.add_transition('restart',['true_ending','bad_ending','pandemic_ending'],'story_begin')
        self.machine.add_transition('talk','homeless_man','true_ending',conditions='trigger_true_ending', unless='trigger_good_ending')
        self.machine.add_transition('talk','homeless_man','good_ending',conditions='trigger_good_ending')
    
        # SECTION shelter2 states
        self.machine.add_transition('go_to_shelter2','story_begin','shelter2')
        self.machine.add_transition('leave','shelter2','choose_new_dest')        

        # SECTION choose_new_dest transitions
        self.machine.add_transition('go_to_abandoned_city','choose_new_dest','abandoned_city')
        self.machine.add_transition('go_to_mutant_town','choose_new_dest','mutant_town')
        self.machine.add_transition('go_to_shelter2','choose_new_dest','shelter2')

        # SECTION more_info from story_begin
        self.machine.add_transition('see_more_info','story_begin','more_info')
        self.machine.add_transition('go_back_to_game','more_info','story_begin')

        # SECTION functions for on_enter_<state_name>
        for state in self.machine.states:
            call_func_with_str(self.machine,f'on_enter_{state}','print_current_state_text')

    # SECTION entering states related to twists/ resetting variables
    def on_enter_story_begin(self):
        self.reset_game()
    def on_enter_get_bitten(self):
        self.has_been_bitten=True
    def on_enter_dog_eating(self):
        self.has_fed_dog=True
    def on_enter_follow_dialog(self):
        self.asked_sister_to_follow=True
    def on_enter_jewlery_dialog(self):
        self.has_got_jewlery=True
    def on_enter_dialog_with_angry_mutant(self):
        self.angry_mutant_plot_is_triggered=True
    def after_too_slow_transition(self):
        self.user_acted_too_slow=True

    # SECTION conditions for transition
    def trigger_twist_ending(self):
        return self.has_been_bitten
    def trigger_true_ending(self):
        return self.has_got_jewlery
    def reset_game(self):
        self.has_been_bitten=False
        self.has_got_jewlery=False
        self.asked_sister_to_follow=False
        self.has_fed_dog=False
        self.angry_mutant_plot_is_triggered=False
        self.user_acted_too_slow=False
    def trigger_good_ending(self):
        return self.asked_sister_to_follow
    def twist_bad_ending(self):
        return self.has_fed_dog
    def has_triggered_dog_plot(self):
        return self.has_been_bitten or self.has_fed_dog
    # SECTION helper functions for in game textt
    def print_current_state_text(self):
        print_state_text(self.state)
    def get_current_triggers(self):
        # too_slow and automatic transition(to_<state_name>) aren't selectable options
        return [trigger for trigger in  self.machine.get_triggers(self.state) if trigger[0:3]!='to_' and trigger!='too_slow']
    def get_current_options(self):
        return get_options(self.get_current_triggers())
    def has_triggered_angry_mutant_plot(self):
        return self.angry_mutant_plot_is_triggered

# story = Story()
# draw the whole graph ...
# story.get_graph().draw('whole_state_diagram.png', prog='dot')
