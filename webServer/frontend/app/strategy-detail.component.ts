import { Component, Input, OnInit } from '@angular/core';
import { ActivatedRoute, Params }   from '@angular/router';
import { Location }                 from '@angular/common';

import { Strategy }         from './strategy';
import { StrategyService } from './strategy.service';
import 'rxjs/add/operator/switchMap';



@Component({
  moduleId: module.id,
  selector: 'my-strategy-detail',
  templateUrl: 'strategy-detail.component.html',
  styleUrls: [ 'strategy-detail.component.css' ] 
})


export class StrategyDetailComponent implements OnInit {
  strategy: Strategy;
  constructor(
    private strategyService: StrategyService,
    private route: ActivatedRoute,
    private location: Location
  ) {}

  ngOnInit(): void {
    this.route.params
      .switchMap((params: Params) => this.strategyService.getStrategyByName(params['name']))
      .subscribe(strategy => this.strategy = strategy);
  }
  goBack(): void {
    this.location.back();
  }

}

