import { Injectable }       from '@angular/core';
import { DropdownQuestion } from './question-dropdown';
import { Parameter } from './parameter';
import { QuestionBase }     from './question-base';
import { StrategyService } from './strategy.service';
import { Strategy } from './strategy';
import { Transition }         from './transition';
import { TextboxQuestion }  from './question-textbox';

@Injectable()
export class QuestionService {
  // Todo: get from a remote source of question metadata
  // Todo: make asynchronous
  constructor(private strategyService: StrategyService) {
  }
  strategies: Strategy[] = [];

  getNewTransitionQuestions(): QuestionBase<any>[] {
    this.strategyService.getStrategies().then(strategies => this.strategies = strategies);
    let strategiesOptions: {key: string, value: string}[] = [];
    for(let i = 0; i < this.strategies.length; ++i) { 
      strategiesOptions.push({key:this.strategies[i].name, value:this.strategies[i].name});
    }


    let questions: QuestionBase<any>[] = [
      new DropdownQuestion({
        key: 'strategyName',
        label: 'Strategy',
        options: strategiesOptions,
        order: 3
      }),
      new TextboxQuestion({
        key: 'object',
        label: 'Object',
        value: '',
        required: true,
        order: 2
      }),
      new TextboxQuestion({
        key: 'name',
        label: 'Name',
        value: 'newTransition',
        required: true,
        order: 1
      })
    ];
    return questions.sort((a, b) => a.order - b.order);
  }

  getQuestionsFromTrans(transition: Transition): QuestionBase<any>[] {
    this.strategyService.getStrategies().then(strategies => this.strategies = strategies);
    let strategiesOptions: {key: string, value: string}[] = [];
    for(let i = 0; i < this.strategies.length; ++i) { 
      strategiesOptions.push({key:this.strategies[i].name, value:this.strategies[i].name});
    }

    let questions: QuestionBase<any>[] = [
      new TextboxQuestion({
        key: 'object',
        label: 'Object',
        value: transition.object,
	type: 'string',
        order: 2
      }),
      new TextboxQuestion({
        key: 'name',
        label: 'Name',
        value: transition.name,
	type: 'string',
        order: 1
      }),
      new DropdownQuestion({
        key: 'strategyName',
        label: 'Strategy',
	value: transition.strategyName,
        options: strategiesOptions,
        order: 4
      }),
      new TextboxQuestion({
        key: 'duration',
        label: 'Duration',
        value: transition.duration,
	type: 'number',
        order: 3
      })
    ];

    return questions.sort((a, b) => a.order - b.order);
  }

  getQuestionsFromParameters(json: string): QuestionBase<any>[] {
    let questions: QuestionBase<any>[] = [];
    if(typeof json == 'undefined' || json == '')
      return questions;
    let parameters:Parameter[] = JSON.parse(json);
    for (var index in parameters) {
      let textQuestion = new TextboxQuestion({
	                     key: parameters[index].name,
	                     label: parameters[index].name,
	                     value: parameters[index].value,
	                     type: 'string',
	                     order: index
	                   });
      questions.push(textQuestion);
    }

    return questions.sort((a, b) => a.order - b.order);
  }

  
}

