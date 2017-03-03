import { Component, OnInit, ViewChild } from '@angular/core';
import { ModalDirective } from 'ng2-bootstrap';

import { QuestionService } from './question.service';
import { Transition } from './transition';
import { TransitionService } from './transition.service';


@Component({
  selector: 'my-transitions',
  templateUrl: './transitions.component.html',
  styleUrls: [ './transitions.component.css' ]
})

export class TransitionsComponent implements OnInit {

  questions: any[] = [];
  transitions: Transition[] = [];
  newTransitionJson: string;
  isFormChanged: boolean = false;
  errMsg :any;

  @ViewChild('staticModal') public staticModal:ModalDirective;

  constructor(private transitionService: TransitionService, private questionService: QuestionService) { }

  ngOnInit(): void {
      this.transitionService.getTransitions()
          .then(transitions => this.transitions = transitions);
      //TODO: remove following line 
      this.questions = this.questionService.getNewTransitionQuestions();
  }
  goBack(): void {

  }
  public showModal():void {
    this.questions = this.questionService.getNewTransitionQuestions();
    this.staticModal.show();
  }
  public hideModal():void {
    this.staticModal.hide();
  }
  onChange(formValue: string):void{
    this.newTransitionJson = JSON.stringify(formValue);
    this.isFormChanged = true;
  }
  onSubmit():void {
    this.transitionService.addNewTransition(this.newTransitionJson).
          then(transition => { this.transitions.push(transition); this.hideModal();},
               error =>  this.errMsg = <any>error);
    this.isFormChanged = false;
  }
}
